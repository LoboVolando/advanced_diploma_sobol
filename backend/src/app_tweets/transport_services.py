import logging
import random
import typing as t
from abc import ABC, abstractmethod

from .schemas import (
    AuthorSchema,
    MeAuthorOutSchema,
    MeAuthorSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetSchema,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class AbstractTweetService(ABC):
    """адстрактный класс для работы с сервисом твиттов"""

    @abstractmethod
    def get_list(self) -> t.Optional[t.List[TweetSchema]]:
        """
        метод получения списка твитов
        :return: опциональный список твиттов
        """
        ...

    @abstractmethod
    def create_tweet(self, new_tweet: TweetInSchema):
        ...


class AbstractAuthorService(ABC):
    @abstractmethod
    async def me(self, api_key: str) -> MeAuthorOutSchema:
        ...


class TweetMockService(AbstractTweetService):
    async def get_list(self) -> t.Optional[t.List[TweetSchema]]:
        return [
            TweetSchema(
                id=1,
                content="tweet-1",
                author=AuthorSchema(id=1, name="Николай Носов"),
            ),
            TweetSchema(
                id=2,
                content="tweet-2",
                author=AuthorSchema(id=1, name="Николай Гоголь"),
            ),
        ]

    async def create_tweet(self, new_tweet: TweetInSchema) -> TweetOutSchema:
        return TweetOutSchema(result=True, tweet_id=random.randint(1, 300000))


class AuthorMockService(AbstractAuthorService):
    async def me(self, api_key: str) -> MeAuthorOutSchema:
        user = MeAuthorOutSchema(
            result=True,
            user=MeAuthorSchema(
                id=random.randint(1, 300000),
                name="John Doe",
                following=self._get_authors_list(10),
                followers=self._get_authors_list(20),
            ),
        )
        logger.info(user)
        return user

    def _get_authors_list(self, count: int):
        return [
            AuthorSchema(id=random.randint(1, 300000), name=f"Author_{i}")
            for i in range(count)
        ]
