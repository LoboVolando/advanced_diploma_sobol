import logging
import pickle
import typing as t

from sqlalchemy import select, update

from app_users.exceptions import FollowerIsNotUnique
from app_users.models import Author
from app_users.mok_services import AuthorMockService
from db import redis, session

from .schemas import SuccessSchema


class AuthorDbService(AuthorMockService):
    async def me(self, api_key: str):
        logging.info("make postgres query...")
        # token = self.get_token_from_redis_by_api_key(api_key)
        if author := await self.get_author(api_key=api_key):
            logging.info("найден автор в бд %s", author)
            return author

    async def get_author(
        self, author_id: int = None, api_key: str = None, name: str = None
    ):
        """запрос в БД по апи-ключу"""
        logging.info("запрос автора по ИД, ключу или имени")
        if author_id:
            query = select(Author).filter_by(id=author_id)
        elif api_key:
            query = select(Author).filter_by(api_key=api_key)
        elif name:
            query = select(Author).filter_by(name=name)
        else:
            raise ValueError("не передано ничего для работы с БД")
        logging.info("подготовлен запрос: %s")
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                result = qs.scalars().first()
                return result

    async def create_author(self, name: str, api_key: str, password: str):
        author = Author(name=name, api_key=api_key, password=password)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(author)
                await async_session.flush()
                logging.info("создали нового пользователя: %s", author)
                return author

    async def add_follow(self, reading_author: Author, writing_author: Author):
        """сервис фалования автора"""
        logging.info(f"reading: {reading_author.id} :: {reading_author.name}")
        logging.info(f"writing: {writing_author.id} :: {writing_author.name}")
        followers = self._add_author_to_followers(
            reading_author, writing_author
        )
        query = (
            update(Author)
            .where(Author.id == reading_author.id)
            .values(follower=followers)
        )
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
        return SuccessSchema()

    async def remove_follow(
        self, reading_author: Author, writing_author: Author
    ):
        """удаление фоловера из бд"""
        logging.info(f"reading: {reading_author.id} :: {reading_author.name}")
        logging.info(f"writing: {writing_author.id} :: {writing_author.name}")
        followers = self._remove_author_to_followers(
            reading_author, writing_author
        )
        query = (
            update(Author)
            .where(Author.id == reading_author.id)
            .values(follower=followers)
        )
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
        return SuccessSchema()

    def _add_author_to_followers(
        self, reading_author: Author, writing_author: Author
    ) -> t.List[dict]:
        logging.warning("run _add_author_to_followers")
        new_follower = {"id": writing_author.id, "name": writing_author.name}
        if followers := reading_author.follower:
            if new_follower in followers:
                raise FollowerIsNotUnique("неуникальный фоловер")
            followers.append(new_follower)
        else:
            followers = [
                new_follower,
            ]
        return followers

    def _remove_author_to_followers(
        self, reading_author: Author, writing_author: Author
    ) -> list:
        logging.warning("run _add_author_to_followers")
        if followers := reading_author.follower:
            new_follower = {
                "id": writing_author.id,
                "name": writing_author.name,
            }
            try:
                followers.remove(new_follower)
                return followers
            except Exception as e:
                logging.exception(
                    exc_info=e, msg="непредвиденная ошибка удаления фоловера"
                )
                raise FollowerIsNotUnique(
                    "непредвиденная ошибка удаления фоловера"
                )
        else:
            return list()


class AuthorRedisService:
    @classmethod
    async def save_author_model(cls, api_key: str, model: Author):
        try:
            model = pickle.dumps(model)
            await redis.set(api_key, model)
            logging.info("юзер сохранён в редис успешно")
        except Exception as e:
            logging.exception(exc_info=e, msg="ошибка сохранения в редис")

    @classmethod
    async def get_author_model(cls, api_key: str):
        try:
            if author := await redis.get(api_key):
                author = pickle.loads(author)
                logging.info("юзер загружен из редис успешно: %s", author)
                return author
        except Exception as e:
            logging.exception(
                exc_info=e,
                msg=f"ошибка получения пользователя из редис {api_key}",
            )
