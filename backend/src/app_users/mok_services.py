import random
import typing as t

from faker import Faker
from loguru import logger

from app_users.interfaces import AbstractAuthorService
from app_users.schemas import AuthorOutSchema, ProfileAuthorSchema, SuccessSchema
from schemas import ErrorSchema


class AuthorMockService(AbstractAuthorService):
    def __init__(self):
        self.faker = Faker("ru-RU")

    async def me(self, api_key: str) -> ProfileAuthorSchema:
        logger.info("run transport service %s", api_key)
        token = await self.get_token_from_redis_by_api_key(api_key)
        # raise AuthorNotExists()
        return await self.get_author_by_id(token["author_id"])

    async def get_author_by_id(self, author_id: int) -> ProfileAuthorSchema:
        logger.info("run transport service")
        return ProfileAuthorSchema(
            **self.get_fake_author(),
            following=self._get_authors_list(3),
            followers=self._get_authors_list(5),
        )

    async def get_token_from_redis_by_api_key(self, api_key: str):
        """получить токен юзера из редиса"""
        logger.info("run transport service %s", api_key)
        return dict(author_id=1)

    async def add_follow(self, author_id: int, follow_id: int):
        """сервис реального фалования автора"""
        return SuccessSchema()

    async def remove_follow(self, author_id: int, follow_id: int):
        """сервис реального расфалования автора"""
        return SuccessSchema()

    def get_fake_author(self):
        """генерация фейкового автора"""
        return dict(id=random.randint(1, 300000), name=self.faker.name())

    async def error_get_user(self):
        return ErrorSchema(result=False,
                           error_type="USER_NOT_FOUND",
                           error_message="Ошибка. Пользователель не зарегистрирован",
                           )

    def _get_authors_list(self, count: int) -> t.List[AuthorOutSchema]:
        """получить список авторов"""
        return [AuthorOutSchema(**self.get_fake_author()) for i in range(count)]
