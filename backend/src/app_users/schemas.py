"""
schemas.py
----------

Модуль реализует pydantic-схемы для валидации данных и обмена данных между сервисами.

Note
-----
    Большинство схем поддерживают загрузку из орм-моделей
"""
import typing as t

from pydantic import BaseModel


class AuthorBaseSchema(BaseModel):
    """
    Базовая схема автора твитта.

    Arguments
    ---------
    name: str
        Имя автора.
    """

    name: str

    class Config:
        orm_mode = True


class FollowAuthorSchema(AuthorBaseSchema):
    """Схема автора твита для полей followers following

    Arguments
    ---------
    id: int
        Идентификатор автора
    """
    id: int


class RegisterAuthorSchema(AuthorBaseSchema):
    """Схема автора твита, фронтенд->бэкенд для регистрации автора.

    Arguments
    ---------
    password: str
        Сырой пароль для регистрации автора.
    """

    password: str

    class Config:
        orm_mode = True


class AuthorOutSchema(AuthorBaseSchema):
    """Схема автора твита на вывод модели sqlalchemy

    Arguments
    ---------
    id: int
        Идентификатор записи в СУБД.
    password: str
        Хэш пароля.
    api_key: str
        Уникальный идентификатор для фронтенда.
    """

    id: int
    password: str
    api_key: str

    class Config:
        orm_mode = True


class LikeAuthorSchema(AuthorBaseSchema):
    """Схема автора, которая пойдёт в поля followers и following модели автора.

    Arguments
    ---------
    user_id: int
        Идентификатор автора в СУБД.
    """

    user_id: int

    class Config:
        orm_mode = True


class ProfileAuthorSchema(AuthorOutSchema):
    """Схема профиля автора для бэкенда.

    Arguments
    ---------
    followers: list, optional
        Кого читает автор.
    following: list, optional
        Кто читает автора.
    """

    followers: t.Optional[t.List[FollowAuthorSchema]]
    following: t.Optional[t.List[FollowAuthorSchema]]

    class Config:
        orm_mode = True


class ProfileAuthorOutSchema(BaseModel):
    """Схема профиля автора backend->frontend.

    Arguments
    ---------
    result: bool
        Результат выполнения.
    user: ProfileAuthorSchema
        Собственно профиль автора.
    """

    result: bool = True
    user: ProfileAuthorSchema

    class Config:
        orm_mode = True
