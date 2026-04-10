from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Запрос пользователя к LLM.
    """

    prompt: str = Field(
        min_length=1, max_length=50_000, description="Запрос пользователя"
    )
    system: str | None = Field(
        default=None,
        min_length=1,
        max_length=10_000,
        description="Системная инструкция",
    )
    max_history: int = Field(
        default=10,
        ge=0,
        le=20,
        description="Количество сообщений из истории для включения в контекст",
    )
    temperature: float = Field(
        default=1.0, ge=0.0, le=2.0, description='Степень "креативности" модели'
    )


class ChatResponse(BaseModel):
    """
    Ответ, полученный от LLM.
    """

    answer: str = Field(description="Текст ответа LLM.")


class ChatMessagePublic(BaseModel):
    """
    Публичная схема сообщения, которая используется в ответах.
    """

    id: int = Field(description="Идентификатор сообщения")
    role: str = Field(description="Отправитель сообщения (пользователь, LLM)")
    content: str = Field(description="Текст сообщения")
    created_at: datetime = Field(description="Время отправки сообщения")

    model_config = {"from_attributes": True}
