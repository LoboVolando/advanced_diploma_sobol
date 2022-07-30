import logging
import typing as t

from fastapi import Response, Request

from .schemas import TweetSchema, TweetInSchema, TweetOutSchema, MeAuthorOutSchema
from .transport_services import AbstractTweetService, AbstractAuthorService

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO', handlers=[logging.StreamHandler()])


class PermissionService:
    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response
        logger.info('headers patched')
        logger.info(self.request.headers.keys())
        # self.response.headers['Access-Control-Allow-Origin'] = '*'
        # self.response.headers['Access-Control-Allow-Headers'] = '*'
        if api_key := self.request.headers.get('api-key'):
            self.response.headers['api-key'] = api_key
            self.api_key = api_key

    async def get_api_key(self):
        logger.warning(self.request.headers)
        if self.api_key:
            return self.api_key


class TweetService:
    """
    бизнес-логика работы с твиттами
    """

    def __init__(self, service: AbstractTweetService):
        self.service = service

    async def get_list(self) -> t.Optional[t.List[TweetSchema]]:
        return self.service.get_list()

    async def create_tweet(self, new_tweet: TweetInSchema) -> TweetOutSchema:
        return self.service.create_tweet(new_tweet)


class AuthorService:
    """бизнес-логика по работе с авторами твиттов"""

    def __init__(self, service: AbstractAuthorService):
        self.service = service

    async def me(self, api_key: str) -> MeAuthorOutSchema:
        logger.info(f'exec business AuthorService.me {api_key} ')
        return await self.service.me(api_key)
