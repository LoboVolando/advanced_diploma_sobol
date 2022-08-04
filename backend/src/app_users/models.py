from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON

from db import Base


class Author(Base):
    """модель автора твита"""

    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    follower_count = Column(Integer)
    follower = Column(JSON)
    following = Column(JSON)
    soft_delete = Column(Boolean)
