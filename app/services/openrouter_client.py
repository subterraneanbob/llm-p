import httpx

from pydantic import BaseModel

from app.core.errors import OpenRouterError


class OpenRouterMessage(BaseModel):
    """
    Сообщение одной из категорий: сообщение пользователя, ответ LLM, системный промпт.
    """

    role: str
    content: str


class OpenRouterClient:
    """
    Клиент для OpenRouter.ai.
    """

    def __init__(self, base_url: str, api_key: str, app_name: str, site_url: str):
        """
        Создаёт новый клиент OpenRouter.

        Args:
            base_url (str): Базовый URL OpenRouter, например, https://openrouter.ai/api/v1.
            api_key (str): Ключ авторизации (создаётся в сервисе заранее).
            app_name (str): Имя приложения.
            site_url (str): URL приложения.
        """
        self._http_client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": site_url,
                "X-Title": app_name,
            },
        )

    def _parse_message(self, json_response) -> OpenRouterMessage:
        """
        Разбирает ответ от OpenRouter API и возвращает сообщение LLM.

        Args:
            json_response: Ответ от OpenRouter API (ожидается словарь).

        Raises:
            OpenRouterError: Если из полученного ответа не удалось извлечь сообщение.

        Returns:
            OpenRouterMessage: Ответ, полученный от LLM.
        """
        try:
            message = json_response["choices"][0]["message"]
            return OpenRouterMessage(
                role=message["role"],
                content=message["content"],
            )

        except (KeyError, IndexError, TypeError) as ex:
            raise OpenRouterError(
                "Malformed response received from OpenRouter.ai service"
            ) from ex

    async def make_chat_completion(
        self,
        messages: list[OpenRouterMessage],
        model: str,
        temperature: float,
    ) -> OpenRouterMessage:
        """
        Получает ответ LLM с учётом контекста (истории сообщений и нового запроса пользователя).

        Args:
            messages (list[OpenRouterMessage]): Список сообщений, формирующих контекст.
                Например, системная инструкция, затем история взаимодействия пользователя и LLM,
                затем новое пользовательское сообщение.
            model (str): Название LLM, от которой нужно получить ответ.
            temperature (float): Степень "креативности" модели. Чем меньше значение, тем более предсказуем
                результат работы LLM. При значении равном 0, модель всегда выдаёт один и тот же результат
                при одинаковом контексте.

        Raises:
            OpenRouterError: Если не удалось подключиться к OpenRouter.ai, API вернул ошибку
                или ответ в формате, который не удалось разобрать.

        Returns:
            OpenRouterMessage: Ответ, полученный от LLM.
        """

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
        }

        try:
            response = await self._http_client.post("/chat/completions", json=payload)
            response.raise_for_status()

            return self._parse_message(response.json())
        except httpx.HTTPError as ex:
            raise OpenRouterError("Unable to contact OpenRouter.ai service") from ex

    async def close(self):
        """
        Закрывает клиент и освобождает используемые ресурсы.
        """
        await self._http_client.aclose()
