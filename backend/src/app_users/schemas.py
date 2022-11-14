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


class AuthorModelSchema(BaseModel):
    """схема для сериализации орм"""

    id: int
    name: str
    password: str
    api_key: str
    follower_count: int
    followers: list = None
    following: list = None
    soft_delete: bool = False

    class Config:
        orm_mode = True


class AuthorBaseSchema(BaseModel):
    """короткая схема"""

    id: int
    name: str


class AuthorLikeSchema(BaseModel):
    """короткая схема"""

    user_id: int
    name: str


class AuthorProfileSchema(AuthorBaseSchema):
    """полная схема"""

    followers: t.Optional[t.List[AuthorBaseSchema]]
    following: t.Optional[t.List[AuthorBaseSchema]]


class AuthorProfileApiSchema(BaseModel):
    """схема для вывода апи"""

    result: bool
    user: AuthorProfileSchema


class AuthorRegisterSchema(BaseModel):
    """регистрация автора"""

    name: str
    password: str
