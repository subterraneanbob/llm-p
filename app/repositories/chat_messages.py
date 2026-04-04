from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessagesOrmRepo:
    """
    Репозиторий сообщений.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, new_message: ChatMessage):
        """
        Добавляет новое сообщение.

        Args:
            new_message (ChatMessage): Данные нового сообщения.
        """
        self._session.add(new_message)
        await self._session.commit()
        await self._session.refresh()

    async def get_recent_messages(
        self, user_id: int, messages_limit: int
    ) -> list[ChatMessage]:
        """
        Получает список последних сообщений пользователя с указанным идентификатором `user_id`.
        Сообщения будут отсортированы по времени создания, начиная от самого старого.
        Количество сообщений регулируется параметром `messages_limit`.

        Args:
            user_id (int): Уникальный идентификатор пользователя.
            messages_limit (int, optional): Максимальное количество сообщений.

        Returns:
            list[ChatMessage]: Список последних сообщений пользователя.
        """
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.id))
            .limit(messages_limit)
        )
        result = await self._session.scalars(statement)

        recent_messages = list(result.all())
        recent_messages.reverse()

        return recent_messages

    async def delete_all_messages(self, user_id: int):
        """
        Удаляет все сообщения пользователя с указанным идентификатором `user_id`.

        Args:
            user_id (int): Уникальный идентификатор пользователя.
        """
        statement = delete(ChatMessage).where(ChatMessage.user_id == user_id)

        async with self._session.begin():
            self._session.execute(statement)
