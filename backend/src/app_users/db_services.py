"""
db_services.py
--------------

Модуль реализует взаимодействие с базой данных приложения app_users.
"""

import pickle
import typing as t

from loguru import logger
from sqlalchemy import select, update

from app_users.interfaces import AbstractAuthorService
from app_users.models import Author
from app_users.schemas import ProfileAuthorSchema
from db import redis, session
from schemas import SuccessSchema
from exceptions import BackendException, ErrorsList, exc_handler

TTL = 60


class AuthorDbService(AbstractAuthorService):
    """Класс инкапсулирует cruid для модели авторов"""

    @exc_handler(ConnectionRefusedError)
    async def me(self, api_key: str) -> ProfileAuthorSchema:
        """
        Метод возвращает информацию о пользователе по ключу api_key.

        Parameters
        ----------
            api_key: str
                Ключ, передаваемый фронтендом, по которому ищем пользователя.

        Returns
        -------
        ProfileOutSchema
            Pydantic-схема профиля пользователя, валидная для эндпоинта.
        """
        logger.info("make postgres query...")
        # token = self.get_token_from_redis_by_api_key(api_key)
        if author := await self.get_author(api_key=api_key):
            logger.info(f"найден автор в бд {author}")
            return author

    @exc_handler(ConnectionRefusedError)
    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> ProfileAuthorSchema:
        """
        Метод ищет автора по одному из параметров.

        Parameters
        ----------
        author_id: int, optional
            Идентификатор пользователя.
        api_key: str, optional
            Ключ, отправляемый бэкендом.
        name: str, optional
            Имя пользователя.

        Returns
        -------
         ProfileAuthorSchema
            Pydantic-схема профиля автора.
        """
        logger.info("запрос автора по ИД, ключу или имени")
        if author_id:
            query = select(Author).filter_by(id=author_id)
        elif api_key:
            query = select(Author).filter_by(api_key=api_key)
            print(query)
        elif name:
            query = select(Author).filter_by(name=name)
        else:
            raise BackendException(**ErrorsList.incorrect_parameters)
        logger.info("подготовлен запрос...")
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                user = qs.scalars().first()
                if user:
                    return ProfileAuthorSchema.from_orm(user)

    @exc_handler(ConnectionRefusedError)
    async def create_author(self, name: str, api_key: str, password: str) -> t.Optional[Author]:
        """Метод сохраняет нового автора в базе данных

        Parameters
        ----------
        name: str
            Имя нового автора.
        api_key: str
            Уникальный ключ для фронтенда.
        password: str
            Зашифрованный пароль нового автора.

        Returns
        -------
        Author
            SqlAlchemy-модель автора.
        """
        author = Author(name=name, api_key=api_key, password=password)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(author)
                await async_session.flush()
                logger.info(f"создали нового пользователя: {author}")
                return author

    @exc_handler(ConnectionRefusedError)
    async def update_follow(
        self,
        reading_author: ProfileAuthorSchema,
        writing_author: ProfileAuthorSchema,
        followers: dict,
        following: dict,
    ) -> SuccessSchema:
        """

        Parameters
        ----------
        reading_author: ProfileAuthorSchema
            Профиль читающего автора.
        writing_author: ProfileAuthorSchema
            Профиль пишущего автора.
        followers: dict
            Словарь всех писателей пользователя.
        following: dict
            Сроварь всех читателей пользователя.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции
        """

        logger.info(f"reading: {reading_author.id} :: {reading_author.name}")
        logger.info(f"writing: {writing_author.id} :: {writing_author.name}")
        query_r = update(Author).where(Author.id == reading_author.id).values(followers=followers)
        query_w = update(Author).where(Author.id == writing_author.id).values(following=following)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query_r)
                await async_session.execute(query_w)
                await async_session.commit()
        return SuccessSchema()


class AuthorRedisService:
    """Класс инкапсулирует методы по кэшированию авторов в redis."""

    @classmethod
    async def save_author_model(cls, api_key: str, model: Author) -> None:
        """Метод сохраняет SqlAlchemy-model в redis.

        api_key: str
            Уникальный ключ для фронтенда.
        model: Author
            SqlAlchemy-model автора.
        """
        try:
            model = pickle.dumps(model)
            await redis.set(api_key, model, ex=TTL)
            logger.info("юзер сохранён в редис успешно")
        except Exception as e:
            logger.exception(e)
            logger.error("ошибка сохранения в редис")

    @classmethod
    async def get_author_model(cls, api_key: str) -> t.Optional[Author]:
        """Метод возвращает модель автора из redis по api-key.

        Parameters
        ----------
        api_key: str
            Уникальный ключ для фронтенда.
        Returns
        -------
        Author
            Модель автора
        """
        try:
            if author := await redis.get(api_key):
                author = pickle.loads(author)
                logger.info("юзер загружен из редис успешно: %s", author)
                return author
        except Exception as e:
            logger.exception(e)
            logger.error("ошибка получения пользователя из редис %s", api_key)
