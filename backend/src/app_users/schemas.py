import typing as t

from pydantic import BaseModel


class AuthorBaseSchema(BaseModel):
    name: str


class RegisterAuthorSchema(AuthorBaseSchema):
    password: str


class AuthorOutSchema(AuthorBaseSchema):
    """схема автора твита"""
    id: int


class ProfileAuthorSchema(AuthorOutSchema):
    followers: t.Optional[t.List[AuthorOutSchema]]
    following: t.Optional[t.List[AuthorOutSchema]]


class SuccessSchema(BaseModel):
    """схема успешного выполнения чего-либо"""

    result: bool = True


class ProfileAuthorOutSchema(SuccessSchema):
    """выходная схема о юзере"""

    user: ProfileAuthorSchema


class ErrorSchema(BaseModel):
    """схема ошибки"""
    result: bool = False
    error_type: str
    error_message: str
