import typing as t

from pydantic import BaseModel


class AuthorBaseSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RegisterAuthorSchema(AuthorBaseSchema):
    password: str

    class Config:
        orm_mode = True


class AuthorOutSchema(AuthorBaseSchema):
    """схема автора твита"""

    id: int

    class Config:
        orm_mode = True


class LikeAuthorSchema(AuthorBaseSchema):
    """схема автора твита"""

    user_id: int

    class Config:
        orm_mode = True


class ProfileAuthorSchema(AuthorOutSchema):
    followers: t.Optional[t.List[AuthorOutSchema]]
    following: t.Optional[t.List[AuthorOutSchema]]

    class Config:
        orm_mode = True


class SuccessSchema(BaseModel):
    """схема успешного выполнения чего-либо"""

    result: bool = True

    class Config:
        orm_mode = True


class ProfileAuthorOutSchema(SuccessSchema):
    """выходная схема о юзере"""

    user: ProfileAuthorSchema

    class Config:
        orm_mode = True
