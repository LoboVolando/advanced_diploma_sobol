"""
db_services.py
--------------
Модуль реализует классы для взаимодействия между бизнес-логикой и СУБД.
"""
import typing as t

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app_tweets.interfaces import AbstractTweetService
from app_tweets.models import Tweet
from app_tweets.schemas import TweetInSchema, TweetModelSchema, TweetSchema
from app_users.schemas import AuthorModelSchema
from db import session
from exceptions import BackendException, ErrorsList
from schemas import SuccessSchema


class TweetDbService(AbstractTweetService):
    """Класс инкапсулирует cruid-методы для твитов в СУБД."""

    async def get_list(self, author_id: int) -> t.Optional[t.List[TweetModelSchema]]:
        """Метод получает список твитов из СУБД конкретного автора.

        Parameters
        ----------
        author_id: int
            Идентификатор автора в СУБД.

        Returns
        -------
        List[TweetSchema], optional
            Список pydantic-схем твитов автора.
        """

        query = select(Tweet).filter_by(author_id=author_id, soft_delete=False).options(selectinload(Tweet.author))
        async with session() as async_session:
            async with async_session.begin():
                if query_set := await async_session.execute(query):
                    return [TweetModelSchema.from_orm(item) for item in query_set.scalars().all()]

    async def create_tweet(
        self,
        new_tweet: TweetInSchema,
        author_id: int,
        attachments: t.Optional[t.List[str]],
    ) -> TweetModelSchema:
        """
        Метод создаёт новый твит автора.

        Parameters
        ----------
        new_tweet: TweetInSchema,
            Входящая от фронтенда pydantic-схема нового твита.
        author_id: int
            Идентификатор автора в базе.
        attachments: t.List[str], optional
            Ссылки на картинки.

        Returns
        -------
        Tweet
            SqlAlchemy модель нового твита.
        """
        tweet = Tweet(
            content=new_tweet.tweet_data,
            author_id=author_id,
            likes=[],
            soft_delete=False,
            attachments=attachments,
        )
        logger.info(f"new tweet: {tweet}")
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(tweet)
                await async_session.commit()
        tweet = await self.get_tweet_by_id(tweet_id=tweet.id)
        logger.info(f"создали твит: {tweet.id} :: {tweet.content}, medias: {tweet.attachments}, " f"author:")

        return TweetModelSchema.from_orm(tweet)

    # @exc_handler(ConnectionRefusedError)
    async def get_tweet_by_id(self, tweet_id: int) -> t.Optional[TweetModelSchema]:
        """Метод возвращает твит по идентификатору СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.

        Returns
        -------
        TweetSchema
            Pydantic-схема твита.
        """
        logger.info("запрос твитта по идентификатору СУБД.")
        query = select(Tweet).filter_by(id=tweet_id)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                try:
                    result = qs.scalars().first()
                except Exception as e:
                    logger.warning(e)
                    logger.warning(type(e))
                if result:
                    tweet = TweetModelSchema.from_orm(result)
                    logger.warning(tweet)
                    # tweet.author_ = AuthorModelSchema.from_orm(result.author)
                    return tweet
        raise BackendException(**ErrorsList.tweet_not_exists)

    # @exc_handler(ConnectionRefusedError)
    async def delete_tweet(self, tweet_id: int, author_id: int) -> SuccessSchema:
        """Метод удаляет твит по идентификатору СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        author_id: int
            Идентификатор автора в СУБД.

        Returns
        -------
        TweetSchema
            Pydantic-схема твита.

        Note
        ----
        Имеется в виду мягкое удаление через флаг удаления. На самом деле твит остаётся для принятия решения о
        возбуждении уголовного дела по 288 статье УК РФ.
        """
        logger.info("удаляем твит из постгрес")
        query = update(Tweet).filter_by(id=tweet_id, author_id=author_id).values(soft_delete=True)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
                return SuccessSchema()

    # @exc_handler(ConnectionRefusedError)
    async def update_like_in_tweet(self, tweet_id: int, likes: dict) -> SuccessSchema:
        """Метод перезаписывает лайки в СУБД у конкретного твита.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        likes: dict
            Обновлённый набор лайков.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешного выполнения операции.
        """
        query = update(Tweet).where(Tweet.id == tweet_id).values(likes=likes)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
        return SuccessSchema()
