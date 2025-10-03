from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_config import ORM_CLS, ORM_OBJ


async def get_item_by_id(
    session: AsyncSession, orm_cls: ORM_CLS, item_id: int
) -> ORM_OBJ:
    """
    Получает объект из базы данных по его ID.

    Использует асинхронную сессию SQLAlchemy для получения записи.
    Если объект не найден, вызывается исключение `HTTPException 404`.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        orm_cls (ORM_CLS): Класс модели ORM (например, UserORM).
        item_id (int): Идентификатор объекта.

    Returns:
        ORM_OBJ: Найденный объект модели.

    Raises:
        HTTPException 404: Если объект с указанным ID не существует.
    """
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(404, "Item not found")
    return orm_obj


async def add_item(session: AsyncSession, item: ORM_OBJ):
    """
    Добавляет новый объект в базу данных.

    Выполняет операцию `add` и `commit`. Если возникает конфликт уникальности
    (например, попытка создать пользователя с уже существующим именем),
    выбрасывается исключение `HTTPException 409`.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        item (ORM_OBJ): Объект модели ORM для сохранения.

    Raises:
        HTTPException 409: Если запись с такими данными уже существует.
    """
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        # Откат транзакции, чтобы не оставлять частично выполненные изменения
        await session.rollback()
        raise HTTPException(409, "Item already exists")


async def delete_item(session: AsyncSession, item: ORM_OBJ):
    """
    Удаляет объект из базы данных.

    Выполняет удаление объекта и фиксирует транзакцию.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        item (ORM_OBJ): Объект модели ORM для удаления.
    """
    await session.delete(item)
    await session.commit()
