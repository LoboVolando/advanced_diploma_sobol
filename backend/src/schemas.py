"""
schemas.py
----------

Модуль содержит классы для сообщений фронтенду о возникших ошибках
"""
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """Класс определяет базовую схему ошибки

    Parameters
    ----------
    result: bool
        Результат. Для ошибок дефолтное значение False.
    error_type: str
        Тип ошибки.
    error_message: str
        Сообщение об ошибке.
    """

    result: bool = False
    error_type: str
    error_message: str

    class Config:
        orm_mode = True


class SuccessSchema(BaseModel):
    """Схема успешного выполнения какого-либо действия бэкендом"""

    result: bool = True

    class Config:
        orm_mode = True


class ErrorSchemasList:
    """Класс инкапсулирует сообщения об ошибках для фронтенда.

    Parameters
    ----------
    author_not_exists: ErrorSchema
        Pydantic-схема ошибки, автор не существует.
    recursive_follow: ErrorSchema
       Pydantic-схема ошибки, автор подписывается сам на себя.
    """

    author_not_exists = ErrorSchema(
        error_type="AUTHOR_NOT_EXIST", error_message="автор, запросивший операцию, не существует"
    )

    recursive_follow = ErrorSchema(error_type="RECURSIVE_FOLLOW", error_message="автор фолловит сам себя")

    tweet_not_exists = ErrorSchema(
            error_type="TWEET_NOT_EXIST",
            error_message="операции над несуществующим твитом невозможны",
        )

    not_self_tweet_remove = ErrorSchema(
            error_type="TWEET_NOT_BELONGS_TO_AUTHOR",
            error_message="нельзя удалять чужие твиты, редиска",
        )

    double_like = ErrorSchema(
            error_type="DOUBLE_LIKE_ERROR",
            error_message="автор пытался закинуть несколько лайков на твит",
        )

    remove_not_exist_like = ErrorSchema(
            error_type="REMOVE_NOT_EXITS_LIKE",
            error_message="автор  пытался удалить несуществующий лайк на твит",
        )

    media_import_error =  ErrorSchema(
            error_type="MEDIA_IMPORT_ERROR",
            error_message="непредвиденная ошибка сохранения картинки",
        )