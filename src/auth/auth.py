import bcrypt


def hash_password(password: str) -> str:
    """
    Хэширует переданный пароль с использованием алгоритма bcrypt.

    Args:
        password (str): Необработанный текстовый пароль.

    Returns:
        str: Хэшированный пароль в виде строки.
    """
    # Кодируем пароль в байты, так как bcrypt работает с байтами
    password = password.encode()

    # Генерируем случайную "соль" и хэшируем пароль
    password_hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    # Декодируем результат обратно в строку для удобства хранения
    return password_hashed.decode()


def check_password(password: str, password_hashed: str) -> bool:
    """
    Проверяет, совпадает ли введённый пароль с его хэшированной версией.

    Args:
        password (str): Введённый пользователем пароль.
        password_hashed (str): Хэшированный пароль из базы данных.

    Returns:
        bool: True, если пароли совпадают, иначе False.
    """
    # Конвертируем пароль в байты
    password = password.encode()

    # Конвертируем хэшированный пароль в байты
    password_hashed = password_hashed.encode()

    # Выполняем проверку пароля
    return bcrypt.checkpw(password, password_hashed)
