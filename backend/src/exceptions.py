"""
:exception.py
-------------

Модуль содержит исключения для приложения.
"""
import typing as t
from functools import wraps

import structlog

logger = structlog.get_logger()


class BackendException(Exception):
    """
    Базовое исключение. Код 404
    """

    def __init__(self, error_type: str, error_message: str, *args, **kwargs):
        self.result = False
        self.error_type = error_type
        self.error_message = error_message
        logger.error(f"{error_type} :: {error_message}")


class AuthException(BackendException):
    """Ошибка авторизации и прав."""

    ...


class InternalServerException(BackendException):
    """Внутренняя ошибка сервера. Код 500-х"""

    ...


class ErrorsList:
    """Класс инкапсулирует сообщения об ошибках для фронтенда.

    Parameters
    ----------
    author_not_exists: dict
        Pydantic-схема ошибки, автор не существует.
    recursive_follow: dict
       Pydantic-схема ошибки, автор подписывается сам на себя.
    """

    author_not_exists = dict(error_type="AUTHOR_NOT_EXIST", error_message="автор, запросивший операцию, не существует")
    recursive_follow = dict(error_type="RECURSIVE_FOLLOW", error_message="автор фолловит сам себя")
    tweet_not_exists = dict(
        error_type="TWEET_NOT_EXIST", error_message="операции над несуществующим твитом невозможны"
    )
    not_self_tweet_remove = dict(
        error_type="TWEET_NOT_BELONGS_TO_AUTHOR", error_message="нельзя удалять чужие твиты, редиска"
    )
    double_like = dict(error_type="DOUBLE_LIKE_ERROR", error_message="автор пытался закинуть несколько лайков на твит")
    remove_not_exist_like = dict(
        error_type="REMOVE_NOT_EXITS_LIKE", error_message="автор  пытался удалить несуществующий лайк на твит"
    )
    media_import_error = dict(
        error_type="MEDIA_IMPORT_ERROR", error_message="непредвиденная ошибка сохранения картинки"
    )
    incorrect_password = dict(error_type="INCORRECT_PASSWORD", error_message="неверный пароль")
    incorrect_parameters = dict(error_type="INCORRECT_PARAMETERS", error_message="неверные параметры")
    not_authorized = dict(error_type="AUTH_ERROR", error_message="отсутствует api-key в HTTP-заголовке")
    api_key_not_exists = dict(error_type="AUTH_ERROR", error_message="неправильный api-key")
    connection_refused = dict(
        error_type="CON_REFUSED", error_message="соединение с СУБД было сброшено. Проверьте контейнер с СУБД"
    )
    postgres_query_error = dict(error_type="POSTGRES_QUERY_ERROR", error_message="Неверный запрос к БД")
    serialize_error = dict(error_type="PYDANTIC_SERIALIZE_ERROR", error_message="Ошибка сериализации данных")


def exc_handler(ExceptionClass):
    """декоратор для перехвата исключений СУБД"""

    def decorator(func: t.Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ConnectionRefusedError as e:
                logger.exception(event="ошибка соединения с СУБД postgresql", exc_info=e)
                raise InternalServerException(**ErrorsList.connection_refused)
            except Exception as e:
                logger.exception(event="непредвиденное исключение работы с Postgresql", exc_info=e)
                raise BackendException(**ErrorsList.postgres_query_error)

        return wrapper

    return decorator
