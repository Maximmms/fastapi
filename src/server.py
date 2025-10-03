from fastapi import FastAPI

from src.routers.auths import auths_router
from src.routers.advertisements import advertisement_router
from src.routers.users import users_router
from src.core.lifespan import lifespan


app = FastAPI(
    title="Advertisement API",
    description="Сервис объявлений: позволяет пользователям создавать, просматривать, редактировать и удалять объявления.",
    version="1.0.0",
    terms_of_service=None,
    lifespan=lifespan,
)

"""
Настройка маршрутов (роутеров) приложения.

Приложение использует следующие роутеры:
- `users_router`: Работа с пользователями (создание, получение, удаление).
- `advertisement_router`: Работа с объявлениями (создание, поиск, обновление, удаление).
- `auths_router`: Аутентификация пользователей (логин).
"""

# Регистрация роутера для работы с пользователями
app.include_router(users_router, prefix="/src", tags=["Пользователи"])

# Регистрация роутера для работы с объявлениями
app.include_router(advertisement_router, prefix="/src", tags=["Объявления"])

# Регистрация роутера для аутентификации
app.include_router(auths_router, prefix="/src", tags=["Аутентификация"])
