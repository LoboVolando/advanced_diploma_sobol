"""
models.py
---------
Модуль определяет ORM-модель твитов для SqlAlchemy.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db import Base


class Tweet(Base):
    """Модель твита

    Arguments
    ---------
    id: int
        Идентификатор твита в СУБД.
    content: str
        Текст твита. То, ради чего мы здесь не смотря ни на что.
    author_id: int
        Идентификатор автора. Обеспечивает связь один-ко-многим между моделями автора и твита.
    author
        Обратная связь с моделью автора. Позволяет ОРМ-модели твита добраться до автора.
    likes: dict
        Информация о лайках к этому твиту.
    attachments: dict
        Вложения к твиту. Обычно картинки.
    soft_delete: bool
        Флаг мягкого удаления твита из СУБД.
    """

    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="tweets", lazy="joined")
    likes = Column(JSONB, default=[])
    attachments = Column(JSONB, default=[])
    soft_delete = Column(Boolean, default=False)
