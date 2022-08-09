import logging
import random
import string
import typing as t
from fastapi.requests import Request
from fastapi.responses import Response
from passlib.context import CryptContext

from app_users.db_services import AuthorDbService as AuthorTransportService
from app_users.db_services import AuthorRedisService
from app_users.schemas import ProfileAuthorOutSchema, ProfileAuthorSchema
from app_users.exceptions import PasswordIncorrect

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

    @staticmethod
    def hash_password(raw_password: str) -> str:
        """хеширование пароля"""
        return pwd_context.hash(raw_password)

    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool:
        """проверка пароля"""
        logging.info("compare: %s", hashed_password)
        return pwd_context.verify(raw_password, hashed_password)


class AuthorService:
    """бизнес-логика по работе с авторами твиттов"""

    def __init__(self):
        self.service = AuthorTransportService()

    async def get_or_create_user(self, name: str, password: str) -> tuple:
        """регистрация нового пользователя"""
        logging.info('регистрация нового автора: %s', name)
        author = await self.service.get_author(name=name)
        if author:
            logging.info('автор найден!')
            if PermissionService.verify_password(password, author.password):
                logging.info('пароль совпал')
                await AuthorRedisService.SaveAuthorModel(author.api_key, author)
                return author.api_key, False
            logging.info('пароль некорректен')
            raise PasswordIncorrect
        else:
            api_key = self.generate_api_key(64)
            author = await self.service.create_author(name, api_key, PermissionService.hash_password(password))
            await AuthorRedisService.SaveAuthorModel(api_key, author)
            return api_key, True

    async def me(self, api_key: str):
        logger.info("exec business AuthorService.me %s", api_key)
        if user := await AuthorRedisService.GetAuthorModel(api_key):
            return ProfileAuthorOutSchema(result=True, user=ProfileAuthorSchema(id=user.id, name=user.name))
        elif user := await self.service.get_author(api_key=api_key):
            return ProfileAuthorOutSchema(result=True, user=ProfileAuthorSchema(id=user.id, name=user.name))
        logger.error("не найшли юзера по api-key: %s", api_key)
        return await self.service.error_get_user()

    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> ProfileAuthorOutSchema:
        """сервис получения автора по id"""
        logger.info("run business logic")
        result = await self.service.get_author(author_id, api_key, name)
        return ProfileAuthorOutSchema(result=True, user=result)

    async def add_follow(self, follow_author_id: int, api_key: str):
        """сервис фаллования автора"""
        logger.info("run follow service")
        author = await self.service.get_author(api_key=api_key)
        return await self.service.add_follow(
            author_id=author.id, follow_id=follow_author_id
        )

    async def remove_follow(self, follow_author_id: int, api_key: str):
        """сервис разфаллования автора"""
        author = await self.service.get_author(api_key=api_key)
        return await self.service.remove_follow(
            author_id=author.id, follow_id=follow_author_id
        )

    def generate_api_key(self, length: int):
        """генерация случайной строки"""
        char_set = string.ascii_letters + string.ascii_uppercase + string.digits
        api_key = ''.join(random.sample(char_set, length))
        return api_key
