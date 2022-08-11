import logging
import random
import string
import typing as t

from fastapi.requests import Request
from fastapi.responses import Response
from passlib.context import CryptContext

from app_users.db_services import AuthorDbService as AuthorTransportService
from app_users.db_services import AuthorRedisService
from app_users.exceptions import (
    AuthorNotExists,
    FollowerIsNotUnique,
    PasswordIncorrect,
    RecursiveFollower,
)
from app_users.models import Author
from app_users.schemas import (
    ErrorSchema,
    ProfileAuthorOutSchema,
    ProfileAuthorSchema,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PermissionService:
    """сервис проверяет права и токен (ха, которых еще нет)"""

    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response
        logger.info("проверяем права...")
        if api_key := self.request.headers.get("api-key"):
            logger.info("api_key: %s", api_key)
            self.response.headers["api-key"] = api_key
            self.api_key = api_key
        else:
            logging.error("ВНИМАНИЕ, В ЗАГОЛОВКАХ ЗАПРОСА НЕТ api-key!!!")

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
        # todo декомпозировать на 2 функции
        logging.info("регистрация нового автора: %s", name)
        author = await self.service.get_author(name=name)
        if author:
            logging.info("автор найден!")
            if PermissionService.verify_password(password, author.password):
                logging.info("пароль совпал")
                await AuthorRedisService.save_author_model(
                    author.api_key, author
                )
                return author.api_key, False
            logging.info("пароль некорректен")
            raise PasswordIncorrect
        else:
            api_key = self.generate_api_key(64)
            author = await self.service.create_author(
                name, api_key, PermissionService.hash_password(password)
            )
            await AuthorRedisService.save_author_model(api_key, author)
            return api_key, True

    async def me(self, api_key: str):
        logger.info("exec business AuthorService.me %s", api_key)
        if user := await AuthorRedisService.get_author_model(api_key):
            return ProfileAuthorOutSchema(
                result=True,
                user=ProfileAuthorSchema(id=user.id, name=user.name),
            )
        elif user := await self.service.get_author(api_key=api_key):
            return ProfileAuthorOutSchema(
                result=True,
                user=ProfileAuthorSchema(id=user.id, name=user.name),
            )
        logger.error("не найшли юзера по api-key: %s", api_key)
        return await self.service.error_get_user()

    async def get_author(
        self, author_id: int = None, api_key: str = None, name: str = None
    ) -> ProfileAuthorOutSchema:
        """сервис получения автора по id"""
        logger.info("run business logic")
        result = await self.service.get_author(author_id, api_key, name)
        if not result:
            raise AuthorNotExists(f"Автор не существует")
        return ProfileAuthorOutSchema(result=True, user=result)

    async def add_follow(self, writing_author_id: int, api_key: str):
        """сервис фаллования автора"""
        logger.info("run follow service")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(
            author_id=writing_author_id
        )
        try:
            self._check_follower_authors(reading_author, writing_author)
            return await self.service.add_follow(
                reading_author, writing_author
            )
        except AuthorNotExists:
            logging.error("несуществующий фоловер")
            return ErrorSchema(
                result=False,
                error_type="AUTHOR_NOT_EXIST",
                error_message="не существующий автор",
            )
        except RecursiveFollower:
            logging.error("рекурсивное фоллование")
            return ErrorSchema(
                result=False,
                error_type="RECURSIVE_FOLLOWER",
                error_message="рекурсивное фоллование",
            )
        except FollowerIsNotUnique:
            logging.error("неуникальный фоловер")
            return ErrorSchema(
                result=False,
                error_type="NOT_UNICUE_FOLLOWER",
                error_message="не уникальный фолловер",
            )

    async def remove_follow(self, writing_author_id: int, api_key: str):
        """сервис расфаллования автора"""
        logger.info("run follow service")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(
            author_id=writing_author_id
        )
        try:
            self._check_follower_authors(reading_author, writing_author)
            return await self.service.remove_follow(
                reading_author, writing_author
            )
        except AuthorNotExists:
            logging.error("несуществующий фоловер")
            return ErrorSchema(
                result=False,
                error_type="AUTHOR_NOT_EXIST",
                error_message="не существующий автор",
            )
        except RecursiveFollower:
            logging.error("рекурсивное разфоллование")
            return ErrorSchema(
                result=False,
                error_type="RECURSIVE_FOLLOWER",
                error_message="рекурсивное разфоллование",
            )

    def generate_api_key(self, length: int):
        """генерация случайной строки"""
        char_set = (
            string.ascii_letters + string.ascii_uppercase + string.digits
        )
        api_key = "".join(random.sample(char_set, length))
        return api_key

    def _check_follower_authors(
        self,
        reading_author: t.Optional[Author],
        writing_author: t.Optional[Author],
    ):
        """проверяем, есть ли авторы в натуре"""
        if reading_author is None or writing_author is None:
            raise AuthorNotExists("кого-то из авторов не существует")
        if reading_author.id == writing_author.id:
            raise RecursiveFollower(
                "попытка зафоловить/расфоловить самого себя"
            )
