import typing as t

from pydantic import BaseModel, Field

from ..app_users.schemas import AuthorSchema


class AttachmentSchema(BaseModel):
    """схема вложения к твитту"""

    link: str


class TweetSchema(BaseModel):
    """схема вывода твита"""

    id: int
    content: str = Field(example="запомните этот твит")
    attachments: t.Optional[t.List[AttachmentSchema]]
    author: AuthorSchema
    likes: t.Optional[t.List[AuthorSchema]]


class TweetInSchema(BaseModel):
    """схема нового твита"""

    tweet_data: str
    media_ids: t.Optional[t.List[int]]


class TweetOutSchema(BaseModel):
    """схема нового твита"""

    result: bool
    tweet_id: int


class TweetListOutSchema(BaseModel):
    """схема нового твита"""

    result: bool
    tweets: t.Optional[t.List[TweetSchema]]


class SuccessSchema(BaseModel):
    """схема успешного выполнения чего-либо"""

    result: bool = True
