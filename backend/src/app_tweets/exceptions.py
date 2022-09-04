"""
exceptions.py
-------------
Модуль определяет классы исключений для приложения app_tweets.
"""

class TweetBaseException(BaseException):
    """Базовое исключение для сервиса твиттов."""
    ...


class TweetNotExistsException(TweetBaseException):
    """Исключение: твит не существует."""
    ...


class BelongsTweetToAuthorException(TweetBaseException):
    """Исключение: твит не принадлежит автору."""
    ...
