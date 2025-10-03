import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import String, or_, select

from src import crud
from src.dependency import SessionDependency, TokenDependency
from src.models.advertisements import AdvertisementORM
from src.schemas.advertisements import (
    CreateAdvRequest,
    GetAdvResponse,
    SearchAdvResponse,
)
from src.schemas.base import IdResponse
from src.schemas.users import UpdateAdvRequest

advertisement_router = APIRouter()


@advertisement_router.post("/advertisement", response_model=IdResponse)
async def create_advertisement(
    session: SessionDependency, token: TokenDependency, item: CreateAdvRequest
) -> AdvertisementORM:
    """
    Создаёт новое объявление.

    Требует аутентификации. Пользователь создаёт объявление, передавая данные
    через модель `CreateAdvRequest`. Объявление связывается с пользователем
    по его `user_id`.

    Args:
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.
        item (CreateAdvRequest): Входные данные для создания объявления.

    Returns:
        IdResponse: Содержит id созданного объявления.
    """
    adv_dict = item.model_dump(exclude_unset=True)
    adv_orm_obj = AdvertisementORM(**adv_dict, user_id=token.user_id)
    await crud.add_item(session, adv_orm_obj)
    return adv_orm_obj.id_dict


@advertisement_router.get(
    "/advertisement/{advertisement_id}", response_model=GetAdvResponse
)
async def get_advertisement(
    session: SessionDependency, token: TokenDependency, advertisement_id: int
) -> AdvertisementORM:
    """
    Получает информацию об объявлении по его ID.

    Пользователь может получить только своё объявление или если он является админом.

    Args:
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.
        advertisement_id (int): Идентификатор объявления.

    Returns:
        GetAdvResponse: Детали объявления.

    Raises:
        HTTPException 403: Если у пользователя нет прав на просмотр объявления.
    """
    adv_orm_obj = await crud.get_item_by_id(session, AdvertisementORM, advertisement_id)
    if token.user.role == "admin" or adv_orm_obj.user_id == token.user_id:
        return adv_orm_obj.dict
    raise HTTPException(403, "Insufficient privileges")


@advertisement_router.get("/advertisement", response_model=SearchAdvResponse)
async def search_advertisement(
    session: SessionDependency,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    date_posted: Optional[str] = Query(None),
) -> SearchAdvResponse:
    """
    Выполняет поиск объявлений по различным критериям.

    Поддерживает фильтрацию по заголовку, описанию, цене, владельцу и дате публикации.
    Поиск поддерживает подстановочные знаки (`%`).

    Args:
        session (Session): Асинхронная сессия SQLAlchemy.
        title (str): Поиск по заголовку объявления.
        description (str): Поиск по описанию.
        price (str): Поиск по цене.
        owner (str): Поиск по имени владельца.
        date_posted (str): Поиск по дате публикации.

    Returns:
        SearchAdvResponse: Список найденных объявлений.

    Raises:
        HTTPException 400: Если не указан ни один из параметров поиска.
    """
    if not any([title, description, price, owner, date_posted]):
        raise HTTPException(
            status_code=400, detail="At least one search parameter is required"
        )

    conditions = []

    if title:
        # Используем ilike для регистронезависимого поиска
        conditions.append(AdvertisementORM.title.ilike(f"%{title}%"))
    if description:
        conditions.append(AdvertisementORM.description.ilike(f"%{description}%"))
    if price:
        # Цена — это целое число, поэтому сравниваем точно
        conditions.append(AdvertisementORM.price == price)
    if owner:
        conditions.append(AdvertisementORM.owner.ilike(f"%{owner}%"))
    if date_posted:
        try:
            # Пробуем преобразовать строку в дату
            date_obj = datetime.strptime(date_posted, "%Y-%m-%d").date()
            conditions.append(AdvertisementORM.date_posted == date_obj)
        except ValueError:
            # Если дата некорректна, пробуем искать как текстовую строку
            conditions.append(
                AdvertisementORM.date_posted.cast(String).ilike(f"%{date_posted}%")
            )

    # Формируем SQL-запрос с применением всех условий
    query = select(AdvertisementORM).where(or_(*conditions)).limit(10000)

    result = await session.execute(query)
    advs = result.scalars().all()

    return SearchAdvResponse(advs=[GetAdvResponse.model_validate(adv) for adv in advs])


@advertisement_router.patch(
    "/advertisement/{advertisement_id}", response_model=IdResponse
)
async def update_advertisement(
    session: SessionDependency,
    token: TokenDependency,
    advertisement_id: int,
    item: UpdateAdvRequest,
) -> AdvertisementORM:
    """
    Обновляет существующее объявление.

    Пользователь может редактировать только своё объявление или если он является админом.
    Обновляются поля: `title`, `description`.

    Args:
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.
        advertisement_id (int): Идентификатор объявления.
        item (UpdateAdvRequest): Данные для обновления.

    Returns:
        IdResponse: Содержит id обновлённого объявления.

    Raises:
        HTTPException 403: Если у пользователя нет прав на редактирование.
    """
    orm_obj = await crud.get_item_by_id(
        session,
        AdvertisementORM,
        advertisement_id,
    )
    if token.user.role == "admin" or orm_obj.user_id == token.user_id:
        if item.title is not None:
            orm_obj.title = item.title
        if item.description is not None:
            orm_obj.description = item.description

        await crud.update_item(session, orm_obj)
        return {"id": advertisement_id}
    raise HTTPException(403, "Insufficient privileges")


@advertisement_router.delete(
    "/advertisement/{advertisement_id}", response_model=IdResponse
)
async def delete_advertisement(
    session: SessionDependency, token: TokenDependency, advertisement_id: int
) -> AdvertisementORM:
    """
    Удаляет объявление по его ID.

    Пользователь может удалить только своё объявление или если он является админом.

    Args:
        session (Session): Асинхронная сессия SQLAlchemy.
        token (Token): Данные токена аутентификации.
        advertisement_id (int): Идентификатор объявления.

    Returns:
        IdResponse: Содержит id удалённого объявления.

    Raises:
        HTTPException 403: Если у пользователя нет прав на удаление.
    """
    orm_obj = await crud.get_item_by_id(session, AdvertisementORM, advertisement_id)
    if token.user.role == "admin" or orm_obj.user_id == token.user_id:
        await crud.delete_item(session, orm_obj)
        return {"id": advertisement_id}
