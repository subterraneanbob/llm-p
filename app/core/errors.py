class ApplicationBaseError(Exception):
    """
    Базовый класс для собственных исключений приложения.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class OpenRouterError(ApplicationBaseError):
    """
    Ошибка при взаимодействии с сервисом OpenRouter.ai
    """


class UserConflictError(ApplicationBaseError):
    """
    Ошибка при регистрации, если пользователь с заданным e-mail уже существует.
    """

    def __init__(self, email: str):
        super().__init__(f"User with the e-mail {email} already exists.")


class UnauthorizedError(ApplicationBaseError):
    """
    Ошибка авторизации - неверный e-mail или пароль пользователя.
    """

    def __init__(self):
        super().__init__("Invalid credentials.")


class UserNotFound(ApplicationBaseError):
    """
    Ошибка - пользователь не найден.
    """

    def __init__(self, user_id: int):
        super().__init__(f"User with the id {user_id} is not found.")
