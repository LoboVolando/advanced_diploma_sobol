import typing as t

from pydantic import BaseModel, Field

from app_users.schemas import AuthorOutSchema, LikeAuthorSchema


class AttachmentSchema(BaseModel):
    """схема вложения к твитту"""

    link: str


class TweetSchema(BaseModel):
    """схема вывода твита"""

    id: int
    content: str = Field(example="запомните этот твит")
    attachments: t.Optional[t.List[str]]
    author: AuthorOutSchema
    likes: t.Optional[t.List[LikeAuthorSchema]]

    class Config:
        orm_mode = True


class TweetListSchema(BaseModel):
    tweets: t.List[TweetSchema]


class TweetListOutSchema(BaseModel):
    """схема нового твита"""

    result: bool = True
    tweets: t.Optional[t.List[TweetSchema]]

    class Config:
        orm_mode = True


class TweetInSchema(BaseModel):
    """схема нового твита"""

    tweet_data: str
    tweet_media_ids: t.Optional[t.List[int]]
    attachments: t.Optional[t.List[str]]

    class Config:
        orm_mode = True


class TweetOutSchema(BaseModel):
    """схема нового твита"""

    result: bool
    tweet_id: int

    class Config:
        orm_mode = True


class SuccessSchema(BaseModel):
    """схема успешного выполнения чего-либо"""

    result: bool = True

    class Config:
        orm_mode = True


class MediaOrmSchema(BaseModel):
    """схема вывода картинок из базы"""

    id: int
    link: str
    hash: str

    class Config:
        orm_mode = True


class MediaOutSchema(BaseModel):
    """схема вывода картинок из базы"""

    result: bool = True
    media_id: int
