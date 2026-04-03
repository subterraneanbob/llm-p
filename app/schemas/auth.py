from pydantic import BaseModel, EmailStr, Field, SecretStr


class RegisterRequest(BaseModel):
    """
    Запрос регистрации нового пользователя.
    """

    email: EmailStr
    password: SecretStr = Field(min_length=6, max_length=64)


class TokenResponse(BaseModel):
    """
    Ответ при успешной аутентификации пользователя.
    """

    access_token: str
    token_type: str = "bearer"
