from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.models.database import init_orm, close_orm


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекст-менеджер жизненного цикла приложения FastAPI.

    Выполняет инициализацию базы данных при запуске приложения и
    закрывает соединение с БД после завершения работы.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI.

    Yields:
        None: Передаёт управление дальше для запуска приложения.
    """
    print("START")
    # Инициализируем структуру базы данных (создаём таблицы при необходимости)
    await init_orm()

    # Передача управления основному приложению
    yield

    # Завершение работы: закрываем соединение с базой данных
    await close_orm()
    print("FINISH")
