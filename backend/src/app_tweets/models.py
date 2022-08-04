from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app_users.models import Author
from db import Base


class Tweet(Base):
    """модель твита"""

    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey(Author.id), primary_key=True)
    author = relationship(Author, back_populates="tweets", lazy="joined")
    likes = Column(JSON)
    soft_delete = Column(Boolean)
