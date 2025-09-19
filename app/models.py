import datetime
import uuid
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import config
from custom_type import ROLE

engine = create_async_engine(config.PG_DSN)
Session = async_sessionmaker(bind = engine, expire_on_commit = False)


class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {"id":self.id}


class User(Base):
    __tablename__ = "todo_user"
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(
        String(50), unique = True, index = True, nullable = False
    )
    password: Mapped[str] = mapped_column(String(70), nullable = False)
    role: Mapped[ROLE] = mapped_column(String, default = "user")
    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates = "user", cascade = "all, delete-orphan", lazy = "joined"
    )
    advertisement: Mapped[list["Advertisement"]] = relationship("Advertisement", lazy = "joined",
                                                                back_populates = "user")

    @property
    def dict(self):
        return {'id':self.id, 'name':self.name}


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(primary_key = True)
    token: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID, server_default = func.gen_random_uuid(), unique = True
    )
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default = func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(User, back_populates = "tokens", lazy = "joined")


class Advertisement(Base):
    __tablename__ = "advertisement"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    title: Mapped[str] = mapped_column(String, index = True)
    description: Mapped[str] = mapped_column(String, default = None)
    price: Mapped[int] = mapped_column(Integer, index = True)
    owner: Mapped[str] = mapped_column(String, index = True)
    date_posted: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default = func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship("User", back_populates = "advertisements", lazy = "joined")

    @property
    def dict(self):
        return {
            "id":self.id,
            "title":self.title,
            "description":self.description,
            "price":self.price,
            "owner":self.owner,
            "date_posted":self.date_posted.isoformat(),
            "user_id":self.user_id,
        }


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()


ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]