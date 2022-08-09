from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON

from db import Base


class Author(Base):
    """модель автора твита"""

    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True, unique=True)
    password = Column(String(100), index=True, unique=False)
    api_key = Column(String(100), index=True, unique=True)
    follower_count = Column(Integer, default=0)
    follower = Column(JSON, nullable=True)
    following = Column(JSON, nullable=True)
    soft_delete = Column(Boolean, default=False)
