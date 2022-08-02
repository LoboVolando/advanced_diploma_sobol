import typing as t

from pydantic import BaseModel


class AuthorSchema(BaseModel):
    """схема автора твита"""

    id: int
    name: str


class ProfileAuthorSchema(AuthorSchema):
    followers: t.List[AuthorSchema]
    following: t.List[AuthorSchema]


class ProfileAuthorOutSchema(BaseModel):
    """выходная схема о юзере"""

    result: bool = True
    user: ProfileAuthorSchema


class SuccessSchema(BaseModel):
    """схема успешного выполнения чего-либо"""

    result: bool = True
