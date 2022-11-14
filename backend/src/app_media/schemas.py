"""
schemas.py
----------
Модуль реализует pydantic-схемы для валидации данных и обмена данных между сервисами.

Note
----
Большинство схем поддерживают загрузку из орм-моделей.


"""
from pydantic import BaseModel


class MediaOrmSchema(BaseModel):
    """Pydantic-схема вывода модели orm

    Parameters
    ----------
    id: int
        Идентификатор ресурса в СУБД.
    link: str
        Ссылка для загрузки.
    hash: str
        Хэш, обеспечивающий уникальность файла в СУБД.
    """

    id: int
    link: str
    hash: str

    class Config:
        orm_mode = True


class MediaOutSchema(BaseModel):
    """Pydantic-схема вывода ресурса для фронтенда.

    Parameters
    ----------
    result: bool
        Флаг успешного выполнения операции.
    media_id: int
        Идентификатор ресурса в СУБД.
    """

    result: bool = True
    media_id: int
