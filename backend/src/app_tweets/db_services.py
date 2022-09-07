"""
db_services.py
--------------
Модуль реализует классы для взаимодействия между бизнес-логикой и СУБД.
"""
import typing as t

from loguru import logger
from sqlalchemy import select, update

from app_tweets.interfaces import AbstractTweetService
from app_tweets.models import Tweet
from app_tweets.schemas import TweetInSchema, TweetSchema
from db import session
from exceptions import BackendException, ErrorsList, exc_handler
from schemas import SuccessSchema


class TweetDbService(AbstractTweetService):
    """Класс инкапсулирует cruid-методы для твитов в СУБД."""

    async def get_list(self, author_id: int) -> t.Optional[t.List[TweetSchema]]:
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
        query = select(Tweet).filter_by(author_id=author_id, soft_delete=False)
        async with session() as async_session:
            async with async_session.begin():
                if query_set := await async_session.execute(query):
                    return [TweetSchema.from_orm(item) for item in query_set.scalars()]

    async def create_tweet(
        self,
        new_tweet: TweetInSchema,
        author_id: int,
        attachments: t.Optional[t.List[str]],
    ) -> Tweet:
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
        logger.info("создали твит: %s", tweet)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(tweet)
                await async_session.commit()
                # created_tweet = TweetSchema.from_orm(tweet)
                # return created_tweet
                # todo не распаковывается модель в схему
                return tweet

    @exc_handler(ConnectionRefusedError)
    async def get_tweet_by_id(self, tweet_id: int) -> t.Optional[TweetSchema]:
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
        query = select(Tweet).filter_by(id=tweet_id, soft_delete=False)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                try:
                    result = qs.scalars().first()
                except Exception as e:
                    logger.warning(e)
                    logger.warning(type(e))
                if result:
                    return TweetSchema.from_orm(result)
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
        logger.info("удаляем твит из постгрес")
        query = update(Tweet).filter_by(id=tweet_id, author_id=author_id).values(soft_delete=True)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
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
        return SuccessSchema()
