import logging

from fastapi.requests import Request
from fastapi.responses import Response

from app_users.mok_services import AuthorMockService as AuthorTransportService
from app_users.schemas import ProfileAuthorOutSchema

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])


class PermissionService:
    """сервис проверяет права и токен (ха, которых еще нет)"""

    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response
        logger.info(self.request.headers.keys())
        if api_key := self.request.headers.get("api-key"):
            self.response.headers["api-key"] = api_key
            self.api_key = api_key
        else:
            self.response.headers["api-key"] = "test"
            self.api_key = "test"

    async def get_api_key(self) -> str:
        """возвращаем ключ из заголовка http"""
        logger.warning(self.request.headers)
        if self.api_key:
            return self.api_key


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

    async def get_author_token_by_api_key(self, api_key: str):
        """сервис получения токена автора по его api_key"""
        return await self.service.get_token_from_redis_by_api_key(api_key)

    async def add_follow(self, follow_author_id: int, api_key: str):
        """сервис фаллования автора"""
        logger.info("run follow service")
        token = await self.service.get_token_from_redis_by_api_key(api_key)
        author_id = token.get("author_id")
        return await self.service.add_follow(
            author_id=author_id, follow_id=follow_author_id
        )

    async def remove_follow(self, follow_author_id: int, api_key: str):
        """сервис разфаллования автора"""
        token = await self.service.get_token_from_redis_by_api_key(api_key)
        author_id = token.get("author_id")
        return await self.service.remove_follow(
            author_id=author_id, follow_id=follow_author_id
        )
