from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db import Base


class Tweet(Base):
    """модель твита"""

    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="tweets", lazy="joined")
    likes = Column(JSONB, default=[])
    attachments = Column(JSONB, default=[])
    soft_delete = Column(Boolean, default=False)


class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    link = Column(String(100))
    hash = Column(String(64), index=True, unique=True)
