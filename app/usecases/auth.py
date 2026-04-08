from app.core.errors import UnauthorizedError, UserConflictError, UserNotFound
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersOrmRepo


class AuthUseCase:
    """
    Бизнес-логика регистрации и авторизации пользователей.
    """

    def __init__(self, users_repo: UsersOrmRepo):
        self._users_repo = users_repo

    async def register(self, email: str, plain_text_password: str) -> User:
        """
        Регистрирует нового пользователя.

        Args:
            email (str): e-mail пользователя.
            plain_text_password (str): Пароль пользователя в открытом виде.

        Raises:
            UserConflictError: Если пользователь с указанным e-mail уже существует.

        Returns:
            User: Профиль нового пользователя.
        """
        existing_user = await self._users_repo.get_user_by_email(email)

        if existing_user:
            raise UserConflictError(email)

        new_user = User(
            email=email,
            password_hash=hash_password(plain_text_password),
            role="user",
        )

        await self._users_repo.create(new_user)

        return new_user

    async def login(self, email: str, plain_text_password: str) -> str:
        """
        Авторизует существующего пользователя и создаёт токен доступа.

        Args:
            email (str): e-mail пользователя.
            plain_text_password (str): Пароль пользователя в открытом виде.

        Raises:
            UnauthorizedError: Если пользователь с указанным e-mail не существует
                или указан неверный пароль.

        Returns:
            str: Токен доступа в виде строки.
        """
        existing_user = await self._users_repo.get_user_by_email(email)

        # Если пользователь не найден, то используем None в качестве значения хеша при проверке.
        # В этом случае проверка пароля никогда не будет успешной, но займёт примерно то же время,
        # что и для верного пароля.
        password_hash = existing_user.password_hash if existing_user else None

        if not verify_password(plain_text_password, password_hash):
            raise UnauthorizedError

        return create_access_token(
            subject=str(existing_user.id), role=existing_user.role
        )

    async def get_user_profile(self, user_id: int) -> User:
        """
        Получает профиль существующего пользователя.

        Args:
            user_id (int): Уникальный идентификатор пользователя.

        Raises:
            UserNotFound: Если пользователь с указанным идентификатором не найден.

        Returns:
            User: Профиль пользователя.
        """
        user = await self._users_repo.get_user_by_id(user_id)

        if not user:
            raise UserNotFound(user_id)

        return user
