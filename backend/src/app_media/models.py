"""
models.py
---------
Модуль определяет ORM-модель медиа-ресурсов для SqlAlchemy.
"""
from sqlalchemy import Column, Integer, String

from db import Base


class Media(Base):
    """Модель медиа-ресурса.

    Parameters
    ----------
    id: int
        Уникальный идентификатор ресурса в СУБД.
    link: str
        Ссылка для загрузки ресурса.
    hash: str
        Хэш от файла для предотвращения повторной загрузки файла.
    """
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    link = Column(String(100))
    hash = Column(String(64), index=True, unique=True)
