import httpx

from app.core.config import settings
from app.core.errors import OpenRouterError


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

    async def make_chat_completion(self, payload: dict) -> dict:
        """
        Получает ответ модели на сообщение пользователя с учётом истории сообщений.

        Args:
            payload (dict): Словарь, который содержит название модели и
            историю сообщений между пользователем и моделью.

        Raises:
            OpenRouterError: OpenRouter API вернул ошибку или не удалось подключиться к сервису.

        Returns:
            dict: Ответ от сервиса в виде словаря.
        """
        try:
            response = await self._http_client.post("/chat/completions", json=payload)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPError:
            raise OpenRouterError("Unable to contact OpenRouter.ai service")


client = OpenRouterClient(
    settings.openrouter_base_url,
    settings.openrouter_api_key,
    settings.openrouter_app_name,
    settings.openrouter_site_url,
)
