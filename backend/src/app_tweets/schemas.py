"""
schemas.py
----------

Модуль реализует pydantic-схемы для валидации данных и обмена данных между сервисами.

Note
-----
    Большинство схем поддерживают загрузку из орм-моделей.
"""

from pydantic import Field

from app_users.schemas import *


class TweetModelSchema(BaseModel):
    """Схема ОРМ модели твита.

    Arguments
    ---------
    id: int
        Идентификатор твита в СУБД.
    content: str
        Умная мысль. Не обязательно умная. Не обязательно мысль.
    author_id: int
        Вторичный ключ для связи один-ко-многим.
    soft_delete: bool
        Флаг удаления твита.
    likes: List[LikeAuthorSchema], optional
        Список авторов, отлайкавших этот твит.
    attachments: t.List[int]
        Список идентификаторов медиа-ресурсов.
    author: AuthorModelSchema.
        Схема ОРМ модели Автора твита.
    """

    id: int
    content: str
    author_id: int
    soft_delete: bool
    likes: t.List[dict] = None
    attachments: t.List[str] = None
    author: AuthorModelSchema = None

    class Config:
        orm_mode = True


class TweetSchema(BaseModel):
    """Схема твита.

    Arguments
    ---------
    id: int
        Идентификатор твита в СУБД.
    content: str
        Умная мысль. Не обязательно умная. Не обязательно мысль.
    attachments: [t.List[str], optional
        Список ссылок на картинки.
    author: AuthorOutSchema
        Автор твита.
    likes: List[LikeAuthorSchema], optional
        Список авторов, отлайкавших этот твит.
    """

    id: int
    content: str = Field(example="запомните этот твит")
    attachments: t.Optional[t.List[str]]
    author: AuthorBaseSchema
    likes: t.Optional[t.List[AuthorLikeSchema]]

    class Config:
        orm_mode = True


class TweetModelOutSchema(BaseModel):
    """Схема списка твитов для фронтенда.

    Parameters
    ----------
    result: bool
        Флаг успешного выполнения.
    tweet: TweetSchema
        твит.

    """

    result: bool = True
    tweet: TweetModelSchema

    class Config:
        orm_mode = True


class TweetListOutSchema(BaseModel):
    """Схема списка твитов для фронтенда.

    Parameters
    ----------
    result: bool
        Флаг успешного выполнения.
    tweets: t.List[TweetSchema], optional
        Список твитов автора.

    """

    result: bool = True
    tweets: t.Optional[t.List[TweetSchema]]

    class Config:
        orm_mode = True


class TweetInSchema(BaseModel):
    """Схема нового твита из фронтенда.

    Parameters
    ----------
    tweet_data: str
        Умные мысли.
    tweet_media_ids: List[int], optional
        Идентификаторы картинок из соответствующей модели.
    attachments: List[str], optional
        Адреса картинок для фронтенда.
    """

    tweet_data: str
    tweet_media_ids: t.Optional[t.List[int]]
    attachments: t.Optional[t.List[str]]

    class Config:
        orm_mode = True


class TweetOutSchema(BaseModel):
    """Схема нового твита для фронтенда.

    Parameters
    ----------
    result: bool
        Флаг успешного выполнения.
    tweet_id: int
        Идентификатор нового твита в СУБД.
    """

    result: bool
    tweet_id: int

    class Config:
        orm_mode = True
