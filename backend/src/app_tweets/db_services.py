"""
db_services.py
--------------
Модуль реализует классы для взаимодействия между бизнес-логикой и СУБД.
"""
import typing as t

import structlog
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app_tweets.interfaces import AbstractTweetService
from app_tweets.models import Tweet
from app_tweets.schemas import TweetInSchema, TweetModelSchema, TweetSchema
from db import session
from exceptions import BackendException, ErrorsList, exc_handler
from schemas import SuccessSchema

structlog.configure(processors=[structlog.processors.JSONRenderer(ensure_ascii=False)])
log = structlog.get_logger()


class TweetDbService(AbstractTweetService):
    """Класс инкапсулирует cruid-методы для твитов в СУБД."""

    @exc_handler(ConnectionRefusedError)
    async def get_list(self, author_id: int) -> t.Optional[t.List[TweetModelSchema]]:
        """Метод получает список твитов из СУБД конкретного автора.

        Parameters
        ----------
        author_id: int
            Идентификатор автора в СУБД.

        Returns
        -------
        List[TweetModelSchema], optional
            Список pydantic-схем ORM модели твитов автора.
        """

        query = select(Tweet).filter_by(author_id=author_id, soft_delete=False).options(selectinload(Tweet.author))
        async with session() as async_session:
            async with async_session.begin():
                if query_set := await async_session.execute(query):
                    return [TweetModelSchema.from_orm(item) for item in query_set.scalars().all()]

    @exc_handler(ConnectionRefusedError)
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
            Pydantic схема ORM модели нового твита.
        """
        tweet = Tweet(
            content=new_tweet.tweet_data,
            author_id=author_id,
            likes=[],
            soft_delete=False,
            attachments=attachments,
        )
        log.info(event="пишем твит в postgres", tweet=new_tweet.dict(), attachments=attachments, author_id=author_id)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(tweet)
                await async_session.commit()
                log.info("создан твит")
        tweet = await self.get_tweet_by_id(tweet_id=tweet.id)
        return TweetModelSchema.from_orm(tweet)

    @exc_handler(ConnectionRefusedError)
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
        logger.info("запрос твитта по идентификатору СУБД.", tweet_id=tweet_id)
        query = select(Tweet).filter_by(id=tweet_id)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                result = qs.scalars().first()
        if result:
            tweet = TweetModelSchema.from_orm(result)
            logger.info("твит запрошен успешно", tweet=tweet.dict())
            return tweet
        raise BackendException(**ErrorsList.tweet_not_exists)

    @exc_handler(ConnectionRefusedError)
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
        query = update(Tweet).filter_by(id=tweet_id, author_id=author_id).values(soft_delete=True)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
                logger.info("удаляем твит из postgresql", tweet_id=tweet_id, author_id=author_id)
                return SuccessSchema()

    @exc_handler(ConnectionRefusedError)
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
                logger.info("обновляем лаек автора в postgresql", tweet_id=tweet_id, likes=likes)
        return SuccessSchema()
