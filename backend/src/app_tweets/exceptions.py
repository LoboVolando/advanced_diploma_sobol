class ApiBaseException(BaseException):
    """базовое исключение для бэкенда"""

    ...


class TweetBaseException(ApiBaseException):
    """базовое исключение для сервиса твиттов"""

    ...


class TweetNotExists(TweetBaseException):
    """твит не существует"""

    ...


class BelongsTweetToAuthorException(TweetBaseException):
    """ошибка принадлежности твита автору"""
