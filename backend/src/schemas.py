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
