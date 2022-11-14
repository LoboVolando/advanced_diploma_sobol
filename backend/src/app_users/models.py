"""
models.py
=========

Модуль описывает ОРМ-модели авторов для SQLAlchemy.
"""
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db import Base


class Author(Base):
    """Модель автора твита.

    Arguments
    ---------
    id: int
        Идентификатор автора в СУБД
    name: str
        Имя автора.
    password: str
        Хэш пароля автора.
    api_key: str
        Идентификатор автора для фронтенда.
    followers: dict
        Кто читает автора.
    following: dict
        Кого читает автор.
    soft_delete: bool
        Флаг мягкого удаления автора.
    tweets: int
        Связь с ОРМ моделью твитов.
    """

    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True, unique=True)
    password = Column(String(100), index=True, unique=False)
    api_key = Column(String(100), index=True, unique=True)
    follower_count = Column(Integer, default=0)
    followers = Column(JSONB, default=list())
    following = Column(JSONB, default=list())
    soft_delete = Column(Boolean, default=False)
    tweets = relationship("Tweet", back_populates="author")

    def __repr__(self):
        return f"{self.id} :: {self.name}"
