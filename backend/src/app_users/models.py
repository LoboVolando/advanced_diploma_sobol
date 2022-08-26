from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db import Base


class Author(Base):
    """модель автора твита"""

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
