class ApplicationBaseError(Exception):
    """
    Базовый класс для собственных исключений приложения.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
