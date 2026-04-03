from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    """
    Публичная схема пользователя, которая используется в ответах.
    """

    id: int
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}
