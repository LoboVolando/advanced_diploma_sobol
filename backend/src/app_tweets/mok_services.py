import logging
import random
import typing as t

from faker import Faker

from app_tweets.interfaces import AbstractTweetService
from app_tweets.schemas import (
    AuthorOutSchema,
    SuccessSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_users.db_services import AuthorDbService as AuthorService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class TweetMockService(AbstractTweetService):
    def __init__(self):
        self.author = AuthorService()
        self.faker = Faker("ru-RU")

    async def get_list(self, api_key: str) -> t.Optional[t.List[TweetSchema]]:
        await self.author.get_token_from_redis_by_api_key(api_key)
        return [self.fake_tweet() for _ in range(5)]

    async def create_tweet(
        self, new_tweet: TweetInSchema, api_key: str
    ) -> TweetOutSchema:
        """создаём твит"""
        await self.author.get_token_from_redis_by_api_key(api_key)
        return TweetOutSchema(result=True, tweet_id=random.randint(1, 222222))

    async def delete_tweet(self, tweet_id: int, author_id: int):
        """реализация удаления твита"""
        logger.info("run transport service")
        return SuccessSchema()

    def fake_tweet(self) -> TweetSchema:
        """фейковый твит"""
        return TweetSchema(
            id=random.randint(1, 100000),
            content=self.faker.text(),
            author=AuthorOutSchema(**self.author.get_fake_author()),
        )

    async def get_tweet_by_id(self, tweet_id: int) -> TweetSchema:
        """получение твита по id"""
        return TweetSchema(
            id=tweet_id,
            content="content",
            author=AuthorOutSchema(id=1, name="John Doe"),
        )

    async def add_like_to_tweet(
        self, tweet_id: int, author_id: int
    ) -> SuccessSchema:
        """сервис добавления лайка к твиту"""
        return SuccessSchema()

    async def remove_like_from_tweet(
        self, tweet_id: int, author_id: int
    ) -> SuccessSchema:
        """сервис удаления лайка к твиту"""
        return SuccessSchema()
