from __future__ import annotations

import datetime

from pydantic import BaseModel


class CreateAdvRequest(BaseModel):
    """
    Модель данных для создания объявления.

    Используется при отправке POST-запроса на создание нового объявления.
    Содержит обязательные поля: заголовок, описание, цена и владелец.
    """

    title: str  # Заголовок объявления
    description: str  # Описание объявления
    price: int  # Цена товара или услуги
    owner: str  # Имя владельца объявления


class GetAdvResponse(BaseModel):
    """
    Модель данных для получения информации об объявлении.

    Используется при ответе на GET-запрос. Включает id, заголовок, описание,
    цену, владельца и дату публикации объявления.
    """

    id: int  # Уникальный идентификатор объявления
    title: str  # Заголовок объявления
    description: str  # Описание объявления
    price: int  # Цена
    owner: str  # Владелец объявления
    date_posted: datetime.datetime  # Дата публикации объявления

    class Config:
        from_attributes = True  # Позволяет создавать модель из ORM-объектов


class SearchAdvRequest(BaseModel):
    """
    Модель данных для запроса списка объявлений по списку ID.

    Используется для фильтрации объявлений по их идентификаторам.
    """

    advs: list[int]  # Список идентификаторов объявлений


class SearchAdvResponse(BaseModel):
    """
    Модель ответа со списком объявлений.

    Используется при выполнении поиска объявлений. Содержит список объектов `GetAdvResponse`.
    """

    advs: list[GetAdvResponse]  # Список объявлений


class SearchParams(BaseModel):
    """
    Модель параметров поиска объявлений.

    Используется для фильтрации объявлений по различным критериям:
    заголовок, описание, цена, владелец и дата публикации.
    """

    title: str | None  # Фильтр по заголовку объявления
    description: str | None  # Фильтр по описанию
    price: str | None  # Фильтр по цене (в виде строки)
    owner: str | None  # Фильтр по имени владельца
    date_posted: datetime.datetime | None  # Фильтр по дате публикации

    def any(self) -> bool:
        """
        Проверяет, были ли указаны какие-либо параметры поиска.

        Returns:
            bool: True, если хотя бы один из параметров не равен None, иначе False.
        """
        return any(
            [self.title, self.description, self.price, self.owner, self.date_posted]
        )
