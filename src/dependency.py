import datetime
import uuid
from email.header import Header
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.database import Session
from src.models.tokens import TokenORM


async def get_session() -> AsyncSession:
    """
    Асинхронная зависимость для получения сессии SQLAlchemy.

    Использует контекстный менеджер `Session` из базы данных,
    чтобы открыть новую сессию и передать её в запрос.

    Yields:
        AsyncSession: Активная асинхронная сессия SQLAlchemy.
    """
    async with Session() as session:
        yield session


# Автоматически предоставляет сессию БД при вызове соответствующего маршрута.
SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]


async def get_token(
    x_token: Annotated[uuid.UUID, Header()], session: SessionDependency
) -> TokenORM:
    """
    Асинхронная зависимость для получения валидного токена из заголовка запроса.

    Выполняет проверку:
    - Существует ли токен в базе данных.
    - Не истёк ли срок его действия (TTL).

    Args:
        x_token (uuid.UUID): Токен, переданный в заголовке запроса.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        TokenORM: Объект токена, если он валиден.

    Raises:
        HTTPException 401: Если токен не найден или истёк.
    """
    # Формируем SQL-запрос: ищем токен по значению и проверяем, не истёк ли срок жизни
    query = select(TokenORM).where(
        TokenORM.token == x_token,
        TokenORM.creation_time
        >= (
            datetime.datetime.now() - datetime.timedelta(seconds=settings.TOKEN_TLL_SEC)
        ),
    )

    # Выполняем запрос и получаем результат
    token = await session.scalar(query)

    # Если токен не найден — ошибка авторизации
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found")

    return token


# Автоматически проверяет наличие и валидность токена.
TokenDependency = Annotated[TokenORM, Depends(get_token)]
