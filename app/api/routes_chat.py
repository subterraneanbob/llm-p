from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_usecase, get_current_user_id
from app.core.errors import OpenRouterError
from app.schemas.chat import ChatMessagePublic, ChatRequest, ChatResponse
from app.usecases.chat import ChatUseCase


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat: ChatUseCase = Depends(get_chat_usecase),
):
    """
    Отправляет запрос пользователя с учётом истории сообщений и получает ответ от LLM.
    """
    try:
        answer = await chat.ask(
            user_id,
            data.prompt,
            data.system,
            data.max_history,
            data.temperature,
        )
        return ChatResponse(answer=answer)
    except OpenRouterError as ex:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ex),
            headers={"Retry-After": "300"},
        ) from ex


@router.get("/history", response_model=list[ChatMessagePublic])
async def get_history(
    user_id: int = Depends(get_current_user_id),
    chat: ChatUseCase = Depends(get_chat_usecase),
):
    """
    Получает всю историю сообщений пользователя.
    """
    return await chat.get_history(user_id)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history(
    user_id: int = Depends(get_current_user_id),
    chat: ChatUseCase = Depends(get_chat_usecase),
):
    """
    Удаляет все сообщения пользователя.
    """
    await chat.delete_history(user_id)
