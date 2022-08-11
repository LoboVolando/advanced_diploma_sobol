class AuthorBaseException(BaseException):
    """базовое исключение для сервиса авторов"""

    ...


class AuthorNotExists(AuthorBaseException):
    """Автор не существует"""

    ...


class PasswordIncorrect(AuthorBaseException):
    """пароль неправильный"""

    ...


class FollowerIsNotUnique(AuthorBaseException):
    """не уникальный фоловер"""


class RecursiveFollower(AuthorBaseException):
    """рекурсивное фоллование"""

    ...


class FollowerIsNotExists(AuthorBaseException):
    """указан несуществующий фоловер"""
