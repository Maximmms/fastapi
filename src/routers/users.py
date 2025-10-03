from fastapi import APIRouter, HTTPException

from src import crud
from src.auth import auth
from src.dependency import SessionDependency, TokenDependency
from src.models.users import UserORM
from src.schemas.base import IdResponse
from src.schemas.users import CreateUserRequest, GetUserResponse, UpdateUserRequest

users_router = APIRouter()


@users_router.post("/user", response_model=IdResponse)
async def create_user(
    user_data: CreateUserRequest, session: SessionDependency
) -> UserORM:
    """
    Создаёт нового пользователя.

    Args:
        user_data (CreateUserRequest): Входные данные для создания пользователя.
        session (Session): Асинхронная сессия SQLAlchemy.

    Returns:
        UserORM: Объект пользователя, включающий только его id.

    Process:
        - Хэширует пароль перед сохранением.
        - Сохраняет пользователя в БД.
    """
    # Преобразуем модель запроса в словарь
    user_dict = user_data.model_dump(exclude_unset=True)

    # Хэшируем пароль перед сохранением в БД
    user_dict["password"] = auth.hash_password(user_dict["password"])

    # Создаём ORM-объект пользователя
    user_orm_obj = UserORM(**user_dict)

    # Сохраняем пользователя в БД
    await crud.add_item(session, user_orm_obj)

    # Возвращаем только id созданного пользователя
    return user_orm_obj.id_dict


@users_router.get("/user/{user_id}", response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependency) -> UserORM:
    """
    Получает информацию о пользователе по его ID.

    Args:
        user_id (int): Идентификатор пользователя.
        session (Session): Асинхронная сессия SQLAlchemy.

    Returns:
        GetUserResponse: Данные пользователя.
    """
    # Получаем пользователя из БД по его ID
    user_orm_obj = await crud.get_item_by_id(session, UserORM, user_id)

    # Возвращаем сериализованный объект пользователя
    return user_orm_obj.dict


@users_router.delete("/user/{user_id}", response_model=IdResponse)
async def delete_user(
    user_id: int, session: SessionDependency, token: TokenDependency
) -> UserORM:
    """
    Удаляет пользователя по его ID.

    Пользователь может удалить только себя или если он является администратором.

    Args:
        user_id (int): Идентификатор удаляемого пользователя.
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.

    Returns:
        IdResponse: Содержит id удалённого пользователя.

    Raises:
        HTTPException 403: Если у пользователя нет прав на удаление.
    """
    # Получаем пользователя из БД
    user_orm_obj = await crud.get_item_by_id(session, UserORM, user_id)

    # Проверяем права доступа
    if token.user.role == "admin" or user_orm_obj.id == token.user_id:
        # Удаляем пользователя из БД
        await crud.delete_item(session, user_orm_obj)
        return {"id": user_orm_obj.id}
    raise HTTPException(403, "Insufficient privileges")


@users_router.patch("/user/{user_id}", response_model=IdResponse)
async def update_user(
    user_id: int,
    session: SessionDependency,
    token: TokenDependency,
    user_data: UpdateUserRequest,
) -> UserORM:
    """
    Обновляет данные пользователя.

    Пользователь может редактировать только себя или если он является администратором.
    Поддерживает обновление имени, пароля и роли.

    Args:
        user_id (int): Идентификатор пользователя.
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.
        user_data (UpdateUserRequest): Новые данные пользователя.

    Returns:
        IdResponse: Содержит id обновлённого пользователя.

    Raises:
        HTTPException 403: Если у пользователя нет прав на редактирование.
    """
    # Получаем пользователя из БД
    user_orm_obj = await crud.get_item_by_id(session, UserORM, user_id)

    # Проверяем права доступа
    if token.user.role == "admin" or user_orm_obj.id == token.user_id:
        # Обновляем поля, если они были переданы
        if user_data.name is not None:
            user_orm_obj.name = user_data.name
        if user_data.password is not None:
            user_orm_obj.password = auth.hash_password(user_data.password)
        if user_data.role is not None:
            user_orm_obj.role = user_data.role

        # Сохраняем изменения
        await crud.update_item(session, user_orm_obj)
        return {"id": user_orm_obj.id}
    raise HTTPException(403, "Insufficient privileges")
