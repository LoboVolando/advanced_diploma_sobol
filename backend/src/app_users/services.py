"""
services.py
-----------
Модуль реализует бизнес-логику приложения app_users.

pwd_context: CryptContext
    Мощное колдунство по борьбе с паролями.

"""
import random
import string
from typing import Optional

import structlog
from fastapi.requests import Request
from fastapi.responses import Response
from passlib.context import CryptContext
from pydantic import ValidationError

from app_users.db_services import AuthorDbService as AuthorTransportService
from app_users.schemas import (
    AuthorBaseSchema,
    AuthorModelSchema,
    AuthorProfileApiSchema,
    AuthorProfileSchema,
)
from exceptions import AuthException, BackendException, ErrorsList
from schemas import SuccessSchema

logger = structlog.get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PermissionService:
    """Класс реализует бизнес-логику работы с правами доступа."""

    def __init__(self, request: Request, response: Response) -> None:
        """Конструктор класса. Получает api-key из запроса и пробрасывает его в ответ.

        Parameters
        ----------
        request: Request
            Запрос сервера.
        response: Response
            Ответ сервера.
        """
        self.request = request
        self.response = response
        self.service = AuthorTransportService()
        if api_key := self.request.headers.get("api-key"):
            structlog.contextvars.bind_contextvars(api_key=api_key)
            logger.info(event="получен api_key из заголовка запроса")
            self.response.headers["api-key"] = api_key
            self.api_key = api_key
        else:
            logger.warning(event="не найден api_key в заголовке запроса")

    async def get_api_key(self) -> Optional[str]:
        """Метод возвращает api-key для фронтенда, если он существует.

        Returns
        -------
        str, optional
            Уникальный api-key для фронтенда.
        """
        if self.api_key:
            logger.info("вернули api-key", api_key=self.api_key)
            structlog.contextvars.bind_contextvars(
                api_key=self.api_key,
            )
            return self.api_key
        logger.warning("пользователь не авторизован")
        raise AuthException(**ErrorsList.not_authorized)

    @staticmethod
    def hash_password(raw_password: str) -> str:
        """Метод рассчитывает хеш для сырого пароля.

        Parameters
        ----------
        raw_password: str
            Сырой пароль пользователя.

        Returns
        -------
        str, optional
            Хэш пароля.
        """
        result = pwd_context.hash(raw_password)
        logger.info(event="сделали хэш пароля", password=result)
        return result

    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool:
        """Метод сравнивает хэш сырого пароля с сохраненным хэшем пользователя в базе данных.

        Parameters
        ----------
        raw_password: str
            Сырой пароль пользователя.
        hashed_password: str
            Хэш пароля из базы данных.

        Returns
        -------
        bool
            True если хэш совпал, иначе Else.
        """
        result = pwd_context.verify(raw_password, hashed_password)
        logger.info(event="результат проверки пароля", result=result)
        return result

    async def verify_api_key(self, api_key: str) -> bool:
        """Метод проверяет наличие ключа в СУБД.

        Parameters
        ----------
        api_key: str
            api-key из заголовка запроса.

        Returns
        -------
        bool
            True если api-key совпал, иначе Else.
        """
        result = await self.service.verify_api_key_exist(api_key)
        logger.info(event="проверка существования api-key в СУБД", result=result)
        return result


class AuthorService:
    """Класс реализует бизнес-логику работы с авторами твитов."""

    def __init__(self) -> None:
        """
        Конструктор класса.

        Note
        ----
        В свойство ``self.service`` должен быть добавлена реализация взаимодействия с базой данных.
        """
        self.service = AuthorTransportService()

    async def get_or_create_user(self, name: str, password: str) -> tuple:
        """Метод получает или создаёт пользователя.

        Parameters
        ----------
        name: str
            Имя пользователя.
        password: str
            Пароль пользователя.

        Returns
        -------
        tuple: str, bool
            api-key для фронтенда и флаг created, означающий, был пользователь создан или запрошен из базы данных.
        """
        if author := await self.service.get_author(name=name):
            logger.info(event="автор уже существует. выполняем авторизацию.", name=name)
            if PermissionService.verify_password(password, author.password):
                logger.info("пароль совпал. возврат api-key и флага творения автора", flag=False)
                return author.api_key, False
            logger.warning(event="введён неверный пароль")
            raise AuthException(**ErrorsList.not_authorized)
        else:
            api_key = self.generate_api_key(64)
            if await self.service.create_author(name, api_key, PermissionService.hash_password(password)):
                logger.info(event="создан новый автор", name=name, password=password, flag=True)
                return api_key, True

    async def me(self, api_key: str) -> AuthorProfileApiSchema:
        """Метод возвращает информацио о текущем пользователе.

        Parameters
        ----------

        api_key: str
            Уникальный идентификатор от фронтенда.

        Returns
        -------
        ProfileAuthorOutSchema
            Pydantic-схема профиля пользователя.
        """
        if user := await self.service.get_author(api_key=api_key):
            try:
                result = AuthorProfileApiSchema(
                    result=True,
                    user=AuthorProfileSchema(**user.dict(include={"id", "name", "followers", "following"})),
                )
            except ValidationError as e:
                logger.exception(event="ошибка сериализации", exc_info=e)
                raise BackendException(**ErrorsList.serialize_error)
            else:
                logger.info(event="запрос собственного профиля выполнен успешно", result=result.dict())
                return result
        logger.warning(event="не нашли юзера по api-key")
        raise BackendException(**ErrorsList.author_not_exists)

    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> AuthorProfileApiSchema:
        """Метод возвращает информацио о пользователе по одному из параметров.

        Parameters
        ----------
        author_id: int
            Идентификатор пользователя в базе.
        api_key: str
            Уникальный идентификатор от фронтенда.
        name: str
            Имя пользователя.

        Returns
        -------
        ProfileAuthorOutSchema
            Pydantic-схема профиля пользователя.
        """
        logger.info("запрос автора по параметрам", author_id=author_id, api_key=api_key, name=name)
        if user := await self.service.get_author(author_id, api_key, name):
            try:
                result = AuthorProfileApiSchema(
                    result=True,
                    user=AuthorProfileSchema(**user.dict(include={"id", "name", "followers", "following"})),
                )
            except ValidationError as e:
                logger.exception(event="ошибка сериализации", exc_info=e)
                raise BackendException(**ErrorsList.serialize_error)
            else:
                logger.info(event="ответ сериализован успешно", result=result.dict())
                return result
        logger.error("пользователь не найден")
        raise BackendException(**ErrorsList.postgres_query_error)

    async def add_follow(self, writing_author_id: int, api_key: str) -> SuccessSchema:
        """Метод добавляет читателя к пишущему автору, а писателя - в список авторов читателя.

        Parameters
        ----------
        writing_author_id: int
            Идентификатор пишущего автора в базе данных.
        api_key: str
            Фронтенд-идентификатор текущего пользователя.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции
        """
        logger.info("добавим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        self._check_follower_authors(reading_author, writing_author)

        followers = reading_author.followers
        new_follower = AuthorBaseSchema(id=writing_author.id, name=writing_author.name)
        if new_follower not in followers:
            followers.append(new_follower.dict())
        following = writing_author.following
        new_following = AuthorBaseSchema(id=reading_author.id, name=reading_author.name)
        if new_following not in following:
            following.append(new_following.dict())

        result = await self.service.update_follow(
            reading_author=reading_author,
            writing_author=writing_author,
            followers=followers,
            following=following,
        )
        logger.info(
            event="добавлен фоловер",
            result=result,
            new_follower=new_follower.dict(),
            new_following=new_following.dict,
            followers=followers,
            following=following,
        )
        return result

    async def remove_follow(self, writing_author_id: int, api_key: str) -> SuccessSchema:
        """Метод удаляет читателя из списка читателей пишущего автора, а писателя из список авторов у читателя.

        Parameters
        ----------
        writing_author_id: int
            Идентификатор пишущего автора в базе данных.
        api_key: str
            Фронтенд-идентификатор текущего пользователя.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции
        """
        logger.info("удалим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        self._check_follower_authors(reading_author, writing_author)
        followers = reading_author.dict(include={"followers"}).get("followers", [])

        new_follower = AuthorBaseSchema(id=writing_author.id, name=writing_author.name)
        if new_follower.dict() in followers:
            followers.remove(new_follower.dict())

        following = writing_author.dict(include={"following"}).get("following", [])
        new_following = AuthorBaseSchema(id=reading_author.id, name=reading_author.name)
        if new_following.dict() in following:
            following.remove(new_following.dict())

        result = await self.service.update_follow(
            reading_author=reading_author,
            writing_author=writing_author,
            followers=followers,
            following=following,
        )
        logger.info(
            event="удалён фоловер",
            result=result,
            new_follower=new_follower.dict(),
            new_following=new_following.dict,
            followers=followers,
            following=following,
        )

        return result

    def generate_api_key(self, length: int) -> str:
        """Метод генерирует строку заданной длины случайных символов.

        Parameters
        ----------
        length: int
            Длина искомой строки.

        Returns
        -------
        str
            api-key для фронтенда
        """
        char_set = string.ascii_letters + string.ascii_uppercase + string.digits
        key = "".join(random.sample(char_set, length))
        logger.info(event="генерация нового ключа", key=key)
        return key

    def _check_follower_authors(
        self,
        reading_author: Optional[AuthorModelSchema],
        writing_author: Optional[AuthorModelSchema],
    ):
        """
        Внутренний метод проверки авторов перед установлением связей.
        Проверяет существование авторов и ссылки автора на самого себя.

        Raises
        ------
        RecursiveFollowerException
            Подписка автора на самого себя
        AuthorNotExistsException
            Операции с несуществующими авторами
        """
        if reading_author:
            logger.info(event="передан читающий автор", reading_author=reading_author.dict())
        if writing_author:
            logger.info(event="передан пишущий автор", writing_author=writing_author.dict())
        if reading_author is None or writing_author is None:
            logger.error(event="нет читающего или пишущего автора")
            raise BackendException(**ErrorsList.recursive_follow)
        if reading_author.id == writing_author.id:
            logger.error(event="автор follow-ит сам себя")
            raise BackendException(**ErrorsList.recursive_follow)
