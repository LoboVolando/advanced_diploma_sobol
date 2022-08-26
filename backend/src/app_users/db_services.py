import pickle
import typing as t

from app_users.exceptions import FollowerIsNotUnique
from app_users.models import Author
from app_users.mok_services import AuthorMockService
from loguru import logger
from sqlalchemy import select, update

from db import redis, session

from .schemas import ProfileAuthorSchema, SuccessSchema

TTL = 60


class AuthorDbService(AuthorMockService):
    async def me(self, api_key: str):
        logger.info("make postgres query...")
        # token = self.get_token_from_redis_by_api_key(api_key)
        if author := await self.get_author(api_key=api_key):
            logger.info(f"найден автор в бд {author}")
            return author

    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> ProfileAuthorSchema:
        """запрос в БД по апи-ключу"""
        logger.info("запрос автора по ИД, ключу или имени")
        if author_id:
            query = select(Author).filter_by(id=author_id)
        elif api_key:
            query = select(Author).filter_by(api_key=api_key)
            print(query)
        elif name:
            query = select(Author).filter_by(name=name)
        else:
            raise ValueError("не передано ничего для работы с БД")
        logger.info(f"подготовлен запрос...")
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                user = qs.scalars().first()
                if user:
                    return ProfileAuthorSchema.from_orm(user)

    async def create_author(self, name: str, api_key: str, password: str):

        author = Author(name=name, api_key=api_key, password=password)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(author)
                await async_session.flush()
                logger.info(f"создали нового пользователя: {author}")
                return author

    async def update_follow(
        self,
        reading_author: ProfileAuthorSchema,
        writing_author: ProfileAuthorSchema,
        followers: dict,
        following: dict,
    ):
        """сервис фалования автора"""
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
    @classmethod
    async def save_author_model(cls, api_key: str, model: Author):
        try:
            model = pickle.dumps(model)
            await redis.set(api_key, model, ex=TTL)
            logger.info("юзер сохранён в редис успешно")
        except Exception as e:
            logger.exception(exc_info=e, msg="ошибка сохранения в редис")

    @classmethod
    async def get_author_model(cls, api_key: str):
        try:
            if author := await redis.get(api_key):
                author = pickle.loads(author)
                logger.info("юзер загружен из редис успешно: %s", author)
                return author
        except Exception as e:
            logger.exception(e)
            logger.error("ошибка получения пользователя из редис %s", api_key)
