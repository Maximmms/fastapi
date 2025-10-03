from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.auth import auth
from src import crud
from src.dependency import SessionDependency
from src.models.tokens import TokenORM
from src.models.users import UserORM
from src.schemas.login import LoginRequest, LoginResponse

auths_router = APIRouter()


@auths_router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency) -> LoginResponse:
    """
    Эндпоинт для аутентификации пользователя.

    Выполняет проверку логина и пароля. При успешной аутентификации создаёт
    и возвращает токен доступа, связанный с пользователем.

    Args:
        login_data (LoginRequest): Входные данные для входа (логин и пароль).
        session (Session): Асинхронная сессия SQLAlchemy.

    Returns:
        LoginResponse: Объект токена, содержащий его значение и срок действия.

    Raises:
        HTTPException 401: Если имя пользователя или пароль неверны.
    """

    # Формируем SQL-запрос на получение пользователя по имени
    query = select(UserORM).where(UserORM.name == login_data.name)

    # Выполняем запрос и получаем пользователя из БД
    user = await session.scalar(query)

    # Если пользователь не найден — ошибка авторизации
    if user is None:
        raise HTTPException(401, "Invalid credentials")

    # Проверяем хэшированный пароль из БД с переданным пользователем
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    # Создаём новый токен, связанный с пользователем
    token = TokenORM(user_id=user.id)

    # Сохраняем токен в БД
    await crud.add_item(session, token)

    # Возвращаем данные токена пользователю
    return token.dict
