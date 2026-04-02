from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_text_password: str) -> str:
    """
    Преобразует пароль в открытом виде в безопасный хеш для хранения и последующей проверки.

    Args:
        plain_test_password (str): Пароль в открытом виде.

    Returns:
        str: Хеш пароля вместе с солью.
    """
    return pwd_context.hash(plain_text_password)


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Проверяет, что предоставленный в открытом виде пароль соответствует хешу.

    Args:
        plain_text_password (str): Пароль в открытом виде
        hashed_password (str): Хеш пароля

    Returns:
        bool: True, если пароль соответсвует хешу, иначе False.
    """
    return pwd_context.verify(plain_text_password, hashed_password)
