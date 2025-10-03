import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Конфигурационный класс приложения.

    Использует `pydantic.BaseSettings` для автоматического загрузки значений
    из переменных окружения или файла `.env`. Содержит настройки подключения
    к базе данных и параметры токена.
    """

    # Имя базы данных. По умолчанию "app", если не задано в окружении.
    DB_NAME: str = os.getenv("POSTGRES_DB", "app")

    # Пароль для подключения к базе данных. По умолчанию "secret".
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "secret")

    # Хост базы данных (например, localhost или IP контейнера). По умолчанию "localhost".
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")

    # Порт для подключения к PostgreSQL. По умолчанию 5431.
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5431")

    # Имя пользователя для подключения к базе данных. По умолчанию "app".
    DB_USER: str = os.getenv("POSTGRES_USER", "app")

    # Время жизни токена в секундах (TTL). По умолчанию 2 дня (60 * 60 * 48).
    TOKEN_TLL_SEC: int = 60 * 60 * 48

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        env_file_encoding="utf-8",
    )

    def det_db_url(self) -> str:
        """
        Формирует строку подключения к PostgreSQL.

        Использует данные из конфигурации для построения URL в формате:
        postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>

        Returns:
            str: Полная строка подключения к базе данных.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Глобальная экземпляр конфигурации, который используется в других частях приложения
settings = Settings()
