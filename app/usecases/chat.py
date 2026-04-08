from app.core.config import settings
from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessagesOrmRepo
from app.services.openrouter_client import OpenRouterClient, OpenRouterMessage


class ChatUseCase:
    """
    Бизнес-логика взаимодействия с LLM.
    """

    def __init__(
        self,
        chat_messages_repo: ChatMessagesOrmRepo,
        openrouter_client: OpenRouterClient,
    ):
        self._chat_messages_repo = chat_messages_repo
        self._openrouter_client = openrouter_client

    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: str | None,
        max_history: int,
        temperature: float,
    ) -> str:
        """
        Формирует контекст для LLM из системной инструкции, истории сообщений пользователя
        (последние `max_history` сообщений) и запроса пользователя; направляет полученный запрос
        сервису OpenRouter и возвращает ответ, полученный от LLM.

        Args:
            user_id (int): Уникальный идентификатор пользователя, выполняющего запрос.
            prompt (str): Текст запроса пользователя.
            system (str | None): Системная инструкция.
            max_history (int): Количество последних сообщений для включения в контекст.
            temperature (float): Степень "креативности" модели.

        Returns:
            str: Полученный текст ответа LLM.
        """

        # Формируем контекст
        messages = []

        # Системная инструкция
        if system:
            messages.append(OpenRouterMessage(role="system", content=system))

        # История сообщений
        historical_messages = await self._chat_messages_repo.get_recent_messages(
            user_id, max_history
        )
        for message in historical_messages:
            messages.append(
                OpenRouterMessage(role=message.role, content=message.content)
            )

        # Текущий запрос пользователя
        user_prompt = OpenRouterMessage(role="user", content=prompt)
        messages.append(user_prompt)

        # Получаем ответ от LLM
        llm_response = await self._openrouter_client.make_chat_completion(
            messages,
            settings.openrouter_model,
            temperature,
        )

        # Сохраняем сообщение пользователя и ответ LLM
        await self._chat_messages_repo.create(
            ChatMessage(user_id=user_id, **user_prompt)
        )
        await self._chat_messages_repo.create(
            ChatMessage(user_id=user_id, role="assistant", content=llm_response.content)
        )

        return llm_response.content
