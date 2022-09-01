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


class ErrorSchemasList:
    """Класс инкапсулирует сообщения об ошибках для фронтенда.

    Parameters
    ----------
    author_not_exists: ErrorSchema
        Pydantic-схема ошибки, автор не существует.
    recursive_follow: ErrorSchema
       Pydantic-схема ошибки, автор подписывается сам на себя.
    """
    author_not_exists = ErrorSchema(error_type="AUTHOR_NOT_EXIST",
                                    error_message=f"автор, запросивший операцию, не существует")

    recursive_follow = ErrorSchema(error_type="RECURSIVE_FOLLOW",
                                   error_message=f"автор фолловит сам себя")
