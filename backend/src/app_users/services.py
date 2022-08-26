import random
import string
import typing as t

from app_users.db_services import AuthorDbService as AuthorTransportService
from app_users.db_services import AuthorRedisService
from app_users.exceptions import AuthorNotExists, PasswordIncorrect, RecursiveFollower
from app_users.schemas import ErrorSchema, ProfileAuthorOutSchema, ProfileAuthorSchema
from fastapi.requests import Request
from fastapi.responses import Response
from loguru import logger
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PermissionService:
    """сервис проверяет права и токен (ха, которых еще нет)"""

    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response
        logger.info("проверяем права...")
        if api_key := self.request.headers.get("api-key"):
            logger.info(f"api_key: {api_key}")
            self.response.headers["api-key"] = api_key
            self.api_key = api_key
        else:
            logger.error("ВНИМАНИЕ, В ЗАГОЛОВКАХ ЗАПРОСА НЕТ api-key!!!")

    async def get_api_key(self) -> str:
        """возвращаем ключ из заголовка http"""
        if self.api_key:
            logger.warning(self.api_key)
            return self.api_key

    @staticmethod
    def hash_password(raw_password: str) -> str:
        """хеширование пароля"""
        return pwd_context.hash(raw_password)

    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool:
        """проверка пароля"""
        logger.info("compare: %s", hashed_password)
        return pwd_context.verify(raw_password, hashed_password)


class AuthorService:
    """бизнес-логика по работе с авторами твиттов"""

    def __init__(self):
        self.service = AuthorTransportService()

    async def get_or_create_user(self, name: str, password: str) -> tuple:
        """регистрация нового пользователя"""
        # todo декомпозировать на 2 функции
        logger.info("регистрация нового автора: {}")
        author = await self.service.get_author(name=name)
        if author:
            logger.info("автор найден!")
            if PermissionService.verify_password(password, author.password):
                logger.info("пароль совпал")
                await AuthorRedisService.save_author_model(author.api_key, author)
                return author.api_key, False
            logger.info("пароль некорректен")
            raise PasswordIncorrect
        else:
            api_key = self.generate_api_key(64)
            author = await self.service.create_author(name, api_key, PermissionService.hash_password(password))
            await AuthorRedisService.save_author_model(api_key, author)
            return api_key, True

    async def me(self, api_key: str):
        logger.info("exec business AuthorService.me %s", api_key)
        # if user := await AuthorRedisService.get_author_model(api_key):
        #     return ProfileAuthorOutSchema(
        #         result=True,
        #         user=ProfileAuthorSchema(id=user.id, name=user.name),
        #     )
        if user := await self.service.get_author(api_key=api_key):
            return ProfileAuthorOutSchema(
                result=True,
                user=user,
            )
        logger.error("не найшли юзера по api-key: %s", api_key)
        return await self.service.error_get_user()

    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> ProfileAuthorOutSchema:
        """сервис получения автора по id"""
        logger.info("достанем автора...")
        if user := await self.service.get_author(author_id, api_key, name):
            logger.info(user)
            return ProfileAuthorOutSchema(result=True, user=user)
        logger.error("пользователь не найден")

    async def add_follow(self, writing_author_id: int, api_key: str):
        """сервис фаллования автора"""
        logger.info("добавим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        try:
            self._check_follower_authors(reading_author, writing_author)
        except RecursiveFollower:
            return self.make_recursive_follow_response(api_key)

        followers = reading_author.dict(include={"followers"})["followers"]
        new_follower = {"id": writing_author.id, "name": writing_author.name}
        if new_follower not in followers:
            followers.append(new_follower)

        following = writing_author.dict(include={"following"})["following"]
        new_following = {"id": reading_author.id, "name": reading_author.name}
        if new_following not in following:
            following.append(new_following)

        return await self.service.update_follow(
            reading_author=reading_author,
            writing_author=writing_author,
            followers=followers,
            following=following,
        )

    async def remove_follow(self, writing_author_id: int, api_key: str):
        """сервис расфаллования автора"""
        logger.info("удалим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        try:
            self._check_follower_authors(reading_author, writing_author)
        except RecursiveFollower:
            return self.make_recursive_follow_response(api_key)

        followers = reading_author.dict(include={"followers"})["followers"]
        new_follower = {"id": writing_author.id, "name": writing_author.name}
        if new_follower in followers:
            followers.remove(new_follower)

        following = writing_author.dict(include={"following"})["following"]
        new_following = {"id": reading_author.id, "name": reading_author.name}
        if new_following in following:
            following.remove(new_following)

        return await self.service.update_follow(
            reading_author=reading_author,
            writing_author=writing_author,
            followers=followers,
            following=following,
        )

    def generate_api_key(self, length: int):
        """генерация случайной строки"""
        char_set = string.ascii_letters + string.ascii_uppercase + string.digits
        return "".join(random.sample(char_set, length))

    def _check_follower_authors(
        self,
        reading_author: t.Optional[ProfileAuthorSchema],
        writing_author: t.Optional[ProfileAuthorSchema],
    ):
        """проверяем, есть ли авторы в натуре"""
        if reading_author is None or writing_author is None:
            raise AuthorNotExists("кого-то из авторов не существует")
        if reading_author.id == writing_author.id:
            logger.error("автор (%s) follow-ит сам себя ", {reading_author.id})
            raise RecursiveFollower("попытка зафоловить/расфоловить самого себя")

    def make_no_author_exists_response(self, api_key: str):
        logger.error("автор не существует %s", api_key)
        return ErrorSchema(
            error_type="AUTHOR_NOT_EXIST",
            error_message=f"автор, запросивший операцию, не существует {api_key}",
        )

    def make_recursive_follow_response(self, api_key: str):
        logger.error("автор фолловит сам себя: %s", api_key)
        return ErrorSchema(
            error_type="RECURSIVE_FOLLOW",
            error_message=f"автор фолловит сам себя {api_key}",
        )
