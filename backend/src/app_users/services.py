"""
services.py
-----------
Модуль реализует бизнес-логику приложения app_users.

pwd_context: CryptContext
    Мощное колдунство по борьбе с паролями.

"""
import random
import string
import typing as t

from fastapi.requests import Request
from fastapi.responses import Response
from loguru import logger
from passlib.context import CryptContext

from app_users.db_services import AuthorDbService as AuthorTransportService
from app_users.db_services import AuthorRedisService
from app_users.exceptions import AuthorNotExistsException, PasswordIncorrectException, RecursiveFollowerException
from app_users.schemas import ProfileAuthorOutSchema, ProfileAuthorSchema, SuccessSchema

from schemas import ErrorSchemasList, ErrorSchema

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
        logger.info("проверяем права...")
        if api_key := self.request.headers.get("api-key"):
            logger.info(f"api_key: {api_key}")
            self.response.headers["api-key"] = api_key
            self.api_key = api_key
        else:
            logger.error("ВНИМАНИЕ, В ЗАГОЛОВКАХ ЗАПРОСА НЕТ api-key!!!")

    async def get_api_key(self) -> t.Optional[str]:
        """Метод возвращает api-key для фронтенда, если он существует.

        Returns
        -------
        str, optional
            Уникальный api-key для фронтенда.
        """
        if self.api_key:
            logger.warning(self.api_key)
            return self.api_key

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
        return pwd_context.hash(raw_password)

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
        logger.info("compare: %s", hashed_password)
        return pwd_context.verify(raw_password, hashed_password)


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
        # todo декомпозировать на 2 функции, метод сломан
        logger.info("регистрация нового автора: {}")
        author = await self.service.get_author(name=name)
        if author:
            logger.info("автор найден!")
            if PermissionService.verify_password(password, author.password):
                logger.info("пароль совпал")
                await AuthorRedisService.save_author_model(author.api_key, author)
                return author.api_key, False
            logger.info("пароль некорректен")
            raise PasswordIncorrectException
        else:
            api_key = self.generate_api_key(64)
            author = await self.service.create_author(name, api_key, PermissionService.hash_password(password))
            await AuthorRedisService.save_author_model(api_key, author)
            return api_key, True

    async def me(self, api_key: str) -> ProfileAuthorOutSchema | ErrorSchema:
        """Метод возвращает информацио о текущем пользователе.

        Parameters
        ----------

        api_key: str
            Уникальный идентификатор от фронтенда.

        Returns
        -------
        ProfileAuthorOutSchema
            Pydantic-схема профиля пользователя.
        ErrorSchema
            Pydantic-схема ошибки выполнения метода.
        """
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
        logger.error("не нашли юзера по api-key: %s", api_key)
        return await self.service.error_get_user()

    async def get_author(self, author_id: int = None, api_key: str = None,
                         name: str = None) -> ProfileAuthorOutSchema | ErrorSchema:
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
        ErrorSchema
            Pydantic-схема ошибки выполнения метода.
        """
        logger.info("достанем автора...")
        if user := await self.service.get_author(author_id, api_key, name):
            logger.info(user)
            return ProfileAuthorOutSchema(result=True, user=user)
        logger.error("пользователь не найден")
        return await self.service.error_get_user()

    async def add_follow(self, writing_author_id: int, api_key: str) -> SuccessSchema | ErrorSchema:
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
        ErrorSchema
            Pydantic-схема ошибки выполнения метода.
        """
        logger.info("добавим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        try:
            self._check_follower_authors(reading_author, writing_author)
        except RecursiveFollowerException:
            logger.error("автор фолловит сам себя: %s", api_key)
            return ErrorSchemasList.recursive_follow

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

    async def remove_follow(self, writing_author_id: int, api_key: str) -> SuccessSchema | ErrorSchema:
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
        ErrorSchema
            Pydantic-схема ошибки выполнения метода.
        """
        logger.info("удалим follower")
        reading_author = await self.service.get_author(api_key=api_key)
        writing_author = await self.service.get_author(author_id=writing_author_id)
        try:
            self._check_follower_authors(reading_author, writing_author)
        except RecursiveFollowerException:
            logger.error("автор фолловит сам себя: %s", api_key)
            return ErrorSchemasList.recursive_follow

        followers = reading_author.dict(include={"followers"}).get("followers", [])
        new_follower = {"id": writing_author.id, "name": writing_author.name}
        if new_follower in followers:
            followers.remove(new_follower)

        following = writing_author.dict(include={"following"}).get("following", [])
        new_following = {"id": reading_author.id, "name": reading_author.name}
        if new_following in following:
            following.remove(new_following)

        return await self.service.update_follow(
            reading_author=reading_author,
            writing_author=writing_author,
            followers=followers,
            following=following,
        )

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
        return "".join(random.sample(char_set, length))

    def _check_follower_authors(
            self,
            reading_author: t.Optional[ProfileAuthorSchema],
            writing_author: t.Optional[ProfileAuthorSchema],
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
        if reading_author is None or writing_author is None:
            raise AuthorNotExistsException("кого-то из авторов не существует")
        if reading_author.id == writing_author.id:
            logger.error("автор (%s) follow-ит сам себя ", {reading_author.id})
            raise RecursiveFollowerException("попытка зафоловить/расфоловить самого себя")
