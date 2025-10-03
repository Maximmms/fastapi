from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.database import Base

if TYPE_CHECKING:
    from src.models.users import UserORM


class AdvertisementORM(Base):
    """
    Модель объявления в базе данных.

    Представляет таблицу 'advertisements' и содержит информацию о товарах/услугах,
    включая заголовок, описание, цену, владельца и дату публикации.
    """

    __tablename__ = "advertisements"

    # Заголовок объявления. Уникальное, индексированное поле.
    title: Mapped[str] = mapped_column(String, index=True)

    # Описание объявления. Может быть пустым (default=None).
    description: Mapped[str] = mapped_column(String, default=None)

    # Цена объявления. Целое число, индексированное для быстрого поиска.
    price: Mapped[int] = mapped_column(Integer, index=True)

    # Имя владельца объявления. Индексировано для фильтрации.
    owner: Mapped[str] = mapped_column(String, index=True)

    # Дата публикации объявления. Устанавливается автоматически сервером.
    date_posted: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Внешний ключ к таблице пользователей.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Связь один-ко-многим с моделью User.
    # При удалении пользователя автоматически удаляются связанные объявления.
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="advertisement",
        lazy="joined",
    )

    @property
    def dict(self):
        """
        Возвращает сериализованный словарь с данными объявления.

        Returns:
            dict: Содержит id, заголовок, описание, цену, владельца,
                    дату публикации (в ISO-формате) и идентификатор пользователя.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "owner": self.owner,
            "date_posted": self.date_posted.isoformat(),
            "user_id": self.user_id,
        }
