from app_users.schemas import ProfileAuthorSchema
from app_users.mok_services import AuthorMockService
from app_users.models import Author
from db import session, redis
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
import pickle


class AuthorDbService(AuthorMockService):
    async def me(self, api_key: str):
        logging.info('make postgres query...')
        # token = self.get_token_from_redis_by_api_key(api_key)
        if author := await self.get_author(api_key=api_key):
            logging.info("найден автор в бд %s", author)
            return author

    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None):
        """запрос в БД по апи-ключу"""
        if author_id:
            query = select(Author).filter_by(id=author_id)
        elif api_key:
            query = select(Author).filter_by(api_key=api_key)
        elif name:
            query = select(Author).filter_by(name=name)
        else:
            raise ValueError("не передано ничего для работы с БД")
        logging.info("подготовлен запрос: %s", query)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                return qs.scalars().first()

    async def create_author(self, name: str, api_key: str, password: str):
        author = Author(name=name, api_key=api_key, password=password)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(author)
                await async_session.flush()
                logging.info('создали нового пользователя: %s', author)
                return author


class AuthorRedisService:
    @classmethod
    async def SaveAuthorModel(cls, api_key: str, model: Author):
        try:
            model = pickle.dumps(model)
            await redis.set(api_key, model)
            logging.info('юзер сохранён в редис успешно')
        except Exception as e:
            logging.exception(exc_info=e, msg='ошибка сохранения в редис')

    @classmethod
    async def GetAuthorModel(cls, api_key: str):
        try:
            if author := await redis.get(api_key):
                author = pickle.loads(author)
                logging.info('юзер загружен из редис успешно: %s', author)
                return author
        except Exception as e:
            logging.exception(exc_info=e, msg=f'ошибка получения пользователя из редис {api_key}')
