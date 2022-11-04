"""
db_services.py
--------------

Модуль реализует взаимодействие с базой данных приложения app_users.
"""

import structlog
from sqlalchemy import select, update

from app_users.interfaces import AbstractAuthorService
from app_users.models import Author
from app_users.schemas import *
from db import session
from exceptions import BackendException, ErrorsList, exc_handler
from schemas import SuccessSchema

TTL = 60
logger = structlog.get_logger()


class AuthorDbService(AbstractAuthorService):
    """Класс инкапсулирует cruid для модели авторов"""

    @exc_handler(ConnectionRefusedError)
    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> AuthorModelSchema:
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
        logger.info("запрос автора по ИД, ключу или имени", author_id=author_id, api_key=api_key, name=name)
        if author_id:
            query = select(Author).filter_by(id=author_id)
        elif api_key:
            query = select(Author).filter_by(api_key=api_key)
        elif name:
            query = select(Author).filter_by(name=name)
        else:
            logger.error("неверные параметры")
            raise BackendException(**ErrorsList.incorrect_parameters)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                user = qs.scalars().first()
                if user:
                    result = AuthorModelSchema.from_orm(user)
                    logger.info(event="найден автор", result=result.dict())
                    return result

    @exc_handler(ConnectionRefusedError)
    async def create_author(self, name: str, api_key: str, password: str) -> t.Optional[AuthorModelSchema]:
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
        query = select(Author).filter_by(api_key=api_key)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(author)
                await async_session.flush()
                qs = await async_session.execute(query)
                user = qs.scalars().first()
                if user:
                    result = AuthorModelSchema.from_orm(user)
                    logger.info("новый автор сохранен в postgres", result=result.dict())
                    return result

    @exc_handler(ConnectionRefusedError)
    async def update_follow(
        self,
        reading_author: AuthorModelSchema,
        writing_author: AuthorModelSchema,
        followers: list,
        following: list,
    ) -> SuccessSchema:
        """Метод обновляет фоловеров и фоловингов.

        Parameters
        ----------
        reading_author: ProfileAuthorSchema
            Профиль читающего автора.
        writing_author: ProfileAuthorSchema
            Профиль пишущего автора.
        followers: list
            Список словарей всех писателей пользователя.
        following: list
            Список словарей всех читателей пользователя.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции
        """

        logger.info(event="обновление фоловеров и фоловингов", followers=followers, following=following)
        query_r = update(Author).where(Author.id == reading_author.id).values(followers=followers)
        query_w = update(Author).where(Author.id == writing_author.id).values(following=following)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query_r)
                await async_session.execute(query_w)
                await async_session.commit()
        result = SuccessSchema()
        logger.info(event="успешное завершение")
        return result

    @exc_handler(ConnectionRefusedError)
    async def verify_api_key_exist(self, api_key: str) -> bool:
        """Метод проверяет существование api-key

        Parameters
        ----------
        api_key: str
            Ключ из заголовка запроса.
        """
        query = select(Author.api_key).filter_by(api_key=api_key)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                user = qs.scalars().first()
                if user:
                    logger.info(event="существование api-key подтверждено")
                    return True
                logger.info(event="api-key не существует")
                return False
