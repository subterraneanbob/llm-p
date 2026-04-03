from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Запрос пользователя к LLM.
    """

    prompt: str = Field(min_length=1, max_length=50_000)
    system: str | None = Field(default=None, min_length=1, max_length=10_000)
    max_history: int = Field(default=10, ge=0, le=20)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    """
    Ответ, полученный от LLM.
    """

    answer: str
