import logging
import random
import typing as t
from abc import ABC, abstractmethod

from faker import Faker

from .schemas import (
    AuthorSchema,
    ProfileAuthorSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetSchema,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class AbstractTweetService(ABC):
    """адстрактный класс для работы с сервисом твиттов"""

    @abstractmethod
    def get_list(self, api_key: str):
        """
        метод получения списка твитов
        :return: опциональный список твиттов
        """
        ...

    @abstractmethod
    def create_tweet(self, new_tweet: TweetInSchema, author_id: int):
        """абстрактный метод сохранения твита"""
        ...


class AbstractAuthorService(ABC):
    @abstractmethod
    async def me(self, api_key: str):
        """абстрактный метод получения автора по ключу"""
        ...

    @abstractmethod
    async def get_author_by_id(self, author_id: int):
        """абстрактный метод получения автора по id"""
        ...


class TweetMockService(AbstractTweetService):
    def __init__(self):
        self.author = AuthorMockService()
        self.faker = Faker('ru-RU')

    async def get_list(self, api_key: str) -> t.Optional[t.List[TweetSchema]]:
        token = await self.author.get_token_from_redis_by_api_key(api_key)
        return [self.fake_tweet() for _ in range(5)]

    async def create_tweet(self, new_tweet: TweetInSchema, api_key: str) -> TweetOutSchema:
        """создаём твит"""
        token = await self.author.get_token_from_redis_by_api_key(api_key)
        return TweetOutSchema(result=True, tweet_id=random.randint(1, 222222))

    def fake_tweet(self) -> TweetSchema:
        """фейковый твит"""
        return TweetSchema(
            id=random.randint(1, 100000),
            content=self.faker.text(),
            author=AuthorSchema(**self.author.get_fake_author()),
        )


class AuthorMockService(AbstractAuthorService):

    def __init__(self):
        self.faker = Faker('ru-RU')

    async def me(self, api_key: str) -> ProfileAuthorSchema:
        logger.info('run transport service %s', api_key)
        token = await self.get_token_from_redis_by_api_key(api_key)
        user = await self.get_author_by_id(token['author_id'])
        return user

    async def get_author_by_id(self, author_id: int) -> ProfileAuthorSchema:
        logger.info('run transport service')
        return ProfileAuthorSchema(
            **self.get_fake_author(),
            following=self._get_authors_list(3),
            followers=self._get_authors_list(5),
        )

    async def get_token_from_redis_by_api_key(self, api_key: str):
        """получить токен юзера из редиса"""
        logger.info('run transport service %s', api_key)
        return dict(author_id=random.randint(1, 10000))

    def get_fake_author(self):
        """генерация фейкового автора"""
        return dict(id=random.randint(1, 300000), name=self.faker.name())

    def _get_authors_list(self, count: int) -> t.List[AuthorSchema]:
        """получить список авторов"""
        return [AuthorSchema(**self.get_fake_author()) for i in range(count)]
