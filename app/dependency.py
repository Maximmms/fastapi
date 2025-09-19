import datetime
import uuid
from email.header import Header
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import TOKEN_TLL_SEC
from models import Session, Token

from fastapi import HTTPException


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache = True)]


async def get_token(
        x_token: Annotated[uuid.UUID, Header()],
        session: SessionDependency
) -> Token:
    query = select(Token).where(
        Token.token == x_token,
        Token.creation_time >= (datetime.datetime.now() - datetime.timedelta(seconds = TOKEN_TLL_SEC)),
    )
    token = await session.scalar(query)
    if token is None:
        raise HTTPException(status_code = 401, detail = "Token not found")
    return token

TokenDependency = Annotated[Token, Depends(get_token)]