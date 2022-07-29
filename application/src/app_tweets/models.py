from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship, backref

from ..db import Base


class Author(Base):
    """модель автора твита"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, index=True)
    soft_delete = Column(Boolean)


class Tweet(Base):
    """модель твита"""
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    content = Column(Text(500), nullable=False)
    author = relationship("Author", back_populates="tweets", lazy='joined')
    soft_delete = Column(Boolean)


class Like(Base):
    """связь твитов и пролайкавших авторов"""
    __tablename__ = 'author_liked_tweets_mtm'
    author_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), primary_key=True)
    liked = Column(Boolean())
    liked_authors = relationship(
        'Author', backref=backref('liked_tweets', cascade="all, delete-orphan", lazy='joined'))
    liked_tweets = relationship(
        'Tweet', backref=backref('liked_authors', cascade="all, delete-orphan", lazy='joined'))
