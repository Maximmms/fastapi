from typing import List
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.custom_type import ROLE
from src.models.database import Base

if TYPE_CHECKING:
    from src.models.tokens import TokenORM
    from src.models.advertisements import AdvertisementORM


class UserORM(Base):
    """
    Модель пользователя в базе данных.

    Представляет таблицу 'users' и содержит информацию о пользователе,
    такую как имя, пароль, роль и связанные токены и объявления.
    """

    __tablename__ = "users"

    # Имя пользователя. Уникальное, индексированное, обязательное поле.
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    # Хэшированный пароль пользователя. Обязательное поле.
    password: Mapped[str] = mapped_column(String(70), nullable=False)

    # Роль пользователя (например, 'user', 'admin'). По умолчанию 'user'.
    role: Mapped[ROLE] = mapped_column(String, default="user")

    # Связь один-ко-многим с моделью Token.
    # При удалении пользователя автоматически удаляются все связанные токены.
    tokens: Mapped[List["TokenORM"]] = relationship(
        "TokenORM", back_populates="user", cascade="all, delete-orphan", lazy="joined"
    )

    # Связь один-ко-многим с моделью Advertisement.
    # Загружается вместе с пользователем (lazy="joined").
    advertisement: Mapped[list["AdvertisementORM"]] = relationship(
        "AdvertisementORM", lazy="joined", back_populates="user"
    )

    @property
    def dict(self):
        """
        Преобразует объект в словарь для сериализации.
        """
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "role": self.role,
        }
