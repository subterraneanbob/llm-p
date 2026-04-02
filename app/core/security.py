import time
from datetime import timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _now_seconds() -> int:
    """
    Возвращает целое число секунд, которое прошло с момента начала эпохи (Epoch).

    Returns:
        int: Целое число секунд с начала эпохи.
    """
    return int(time.time())


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


def create_access_token(
    subject: str,
    role: str,
    secret_key: str,
    algorithm: str,
    token_ttl: timedelta,
) -> str:
    """
    Генерирует токен доступа в формате JWT.

    Args:
        subject (str): Субъект, которому принадлежит токен (например, идентификатор пользователя).
        role (str): Роль субъекта (например, роль пользователя - `admin`).
        secret_key (str): Секретный ключ для подписи токена.
        algorithm (str): Алгоритм формирования подписи токена.
        token_ttl (timedelta): Время жизни токена.

    Returns:
        str: Токен доступа в виде JWT строки.
    """
    issued_at = _now_seconds()
    expires_at = issued_at + int(token_ttl.total_seconds())

    claims = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(claims, secret_key, algorithm)


def decode_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    """
    Проверяет JWT токен и возвращает словарь полей, содержащихся в токене, если проверка успешна.

    Args:
        token (str): JWT токен.
        secret_key (str): Секретный ключ, который использовался для подписи токена.
        algorithm (str): Алгоритм формирования подписи токена.

    Returns:
        dict[str, Any]: Словарь полей, указанных в токене.
    """
    return jwt.decode(token, secret_key, algorithm)
