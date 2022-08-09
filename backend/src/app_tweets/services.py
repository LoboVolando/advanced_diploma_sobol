import logging
import typing as t

from app_tweets.exceptions import BelongsTweetToAuthorException
from app_tweets.mok_services import TweetMockService as TweetTransportService
from app_tweets.schemas import (
    TweetInSchema,
    TweetListOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_users.services import AuthorService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class TweetService:
    """
    бизнес-логика работы с твиттами
    """

    def __init__(self):
        self.service = TweetTransportService()

    async def get_list(self, api_key: str) -> TweetListOutSchema:
        logger.info("run service")
        tweets = await self.service.get_list(api_key)
        return TweetListOutSchema(result=True, tweets=tweets)

    async def create_tweet(
            self, new_tweet: TweetInSchema, api_key: str
    ) -> TweetOutSchema:
        """Логика добавления твита"""
        return await self.service.create_tweet(new_tweet, api_key)

    async def delete_tweet(self, tweet_id: int, api_key: str):
        """сервис удаления твита по id"""
        logger.info("run service")
        author_service = AuthorService()
        author = await author_service.get_author(api_key=api_key)
        return await self.service.delete_tweet(
            tweet_id=tweet_id, author_id=author.user.id
        )

    async def add_like_to_tweet(self, tweet_id: int, api_key: str):
        """бизнес-логика добавления лайка"""
        logger.info("run like service")
        author_service = AuthorService()
        author = await author_service.get_author(api_key=api_key)
        return await self.service.add_like_to_tweet(tweet_id, author.user.id)

    async def remove_like_from_tweet(self, tweet_id: int, api_key: str):
        """бизнес-логика добавления лайка"""
        logger.info("run unlike service")
        author_service = AuthorService()
        author = await author_service.get_author(api_key=api_key)
        return await self.service.remove_like_from_tweet(tweet_id, author.user.id)

    async def check_belongs_tweet_to_author(
            self, tweet_id: int, author_id: int
    ) -> t.Optional[bool]:
        """логика проверки принадлежности твита конкретному автору"""
        tweet: TweetSchema = await self.service.get_tweet_by_id(tweet_id)
        if not tweet.author.id == author_id:
            raise BelongsTweetToAuthorException("Твит не принадлежит автору")
        return True
