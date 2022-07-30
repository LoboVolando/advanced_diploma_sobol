import logging
import typing as t

from fastapi import Request, Response

from .schemas import (
    ProfileAuthorOutSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetListOutSchema,
)
from .transport_services import AuthorMockService as AuthorTransportService
from .transport_services import TweetMockService as TweetTransportService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class PermissionService:
    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response
        logger.info(self.request.headers.keys())
        if api_key := self.request.headers.get("api-key"):
            self.response.headers["api-key"] = api_key
            self.api_key = api_key

    async def get_api_key(self):
        """возвращаем ключ из заголовка http"""
        logger.warning(self.request.headers)
        if self.api_key:
            return self.api_key


class TweetService:
    """
    бизнес-логика работы с твиттами
    """

    def __init__(self):
        self.service = TweetTransportService()

    async def get_list(self, api_key: str) -> TweetListOutSchema:
        logger.info('run service')
        tweets = await self.service.get_list(api_key)
        return TweetListOutSchema(result=True, tweets=tweets)

    async def create_tweet(self, new_tweet: TweetInSchema, api_key: str) -> TweetOutSchema:
        return await self.service.create_tweet(new_tweet, api_key)


class AuthorService:
    """бизнес-логика по работе с авторами твиттов"""

    def __init__(self):
        self.service = AuthorTransportService()

    async def me(self, api_key: str) -> ProfileAuthorOutSchema:
        logger.info("exec business AuthorService.me %s", api_key)
        user = await self.service.me(api_key)
        return ProfileAuthorOutSchema(result=True, user=user)

    async def get_author_by_id(self, author_id: int) -> ProfileAuthorOutSchema:
        """сервис получения автора по id"""
        logger.info("run business logic")
        result = await self.service.get_author_by_id(author_id)
        return ProfileAuthorOutSchema(result=True, user=result)
