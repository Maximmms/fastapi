from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.core.config import settings

# Формирование строки подключения к базе данных на основе конфигурации
DATABASE_URL = settings.det_db_url()

# Асинхронный движок SQLAlchemy для взаимодействия с БД
engine = create_async_engine(DATABASE_URL)

# Фабрика асинхронных сессий SQLAlchemy
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    """
    Базовый класс для всех моделей ORM.

    Наследуется от DeclarativeBase и AsyncAttrs для поддержки асинхронной работы.
    Все модели автоматически получают:
    - Поле id как первичный ключ
    - Автоматическое создание имени таблицы (множественное число от имени класса)
    """

    __abstract__ = True  # Указывает, что этот класс не создаст таблицу напрямую

    # Первичный ключ: целое число, автоинкремент
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    @property
    def id_dict(self):
        """
        Возвращает словарь с полем id.

        Returns:
            dict: {"id": <значение>}
        """
        return {"id": self.id}


async def init_orm():
    """
    Инициализирует структуру базы данных.

    Создаёт все таблицы, определённые в моделях, если они ещё не существуют.
    Вызывается при запуске приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def close_orm():
    """
    Закрывает соединение с базой данных.

    Освобождает ресурсы, связанные с движком SQLAlchemy.
    Вызывается при завершении работы приложения.
    """
    await engine.dispose()