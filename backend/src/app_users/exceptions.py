"""
exceptions.py
-------------

Модуль содержит классы исключений приложения app_users.
"""


class AuthorBaseException(BaseException):
    """Базовое исключение для сервиса авторов."""

    ...


class AuthorNotExistsException(AuthorBaseException):
    """Исключение: автор не существует."""

    ...


class PasswordIncorrectException(AuthorBaseException):
    """Исключение: неправильный пароль"""

    ...


class RecursiveFollowerException(AuthorBaseException):
    """Исключение: подписка автора самого на себя"""

    ...
