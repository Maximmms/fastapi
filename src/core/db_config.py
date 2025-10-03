from src.models.advertisements import AdvertisementORM
from src.models.tokens import TokenORM
from src.models.users import UserORM


# Тип объединения ORM-объектов, используемых в приложении.
# Позволяет указывать, что переменная может быть объектом модели:
# - AdvertisementORM (объявление)
# - UserORM (пользователь)
# - TokenORM (токен)
ORM_OBJ = AdvertisementORM | UserORM | TokenORM


# Тип объединения классов ORM-моделей.
# Используется, когда нужно передать класс модели (а не её экземпляр),
# например для операций создания или фильтрации записей в БД.
ORM_CLS = type[AdvertisementORM] | type[UserORM] | type[TokenORM]
