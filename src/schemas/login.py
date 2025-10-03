import uuid

from pydantic import BaseModel

from src.schemas.users import BaseUserRequest


class LoginRequest(BaseUserRequest):
    """
    Модель данных для запроса входа в систему.

    Наследуется от `BaseUserRequest` и содержит обязательные поля:
    имя пользователя и пароль, необходимые для аутентификации.
    """

    name: str  # Имя пользователя (логин)
    password: str  # Пароль, который будет проверяться при входе


class LoginResponse(BaseModel):
    """
    Модель данных для ответа после успешного входа в систему.

    Содержит токен доступа, который используется для аутентификации
    последующих запросов к защищённым эндпоинтам.
    """

    token: uuid.UUID  # Уникальный идентификатор сессии (токен)
