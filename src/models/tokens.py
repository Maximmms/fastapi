import datetime
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.database import Base

if TYPE_CHECKING:
    from src.models.users import UserORM


class TokenORM(Base):
    __tablename__ = "tokens"
    token: Mapped[UUID] = mapped_column(
        UUID, server_default=func.gen_random_uuid(), unique=True
    )
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserORM"] = relationship(
        "UserORM", back_populates="tokens", lazy="joined"
    )
