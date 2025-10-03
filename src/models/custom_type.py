from typing import Literal

# Тип данных ROLE используется для ограничения возможных значений роли пользователя.
# Поддерживает только два значения: "user" и "admin".
ROLE = Literal["user"] | Literal["admin"]
