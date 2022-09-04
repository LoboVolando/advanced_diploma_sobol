"""
services.py
-----------

Модуль определяет бизнес-логику приложения app_tweets.
"""
import typing as t

from loguru import logger

from app_media.services import MediaService
from app_tweets.db_services import TweetDbService as TweetTransportService
from app_tweets.exceptions import BelongsTweetToAuthorException
from app_tweets.schemas import (
    TweetInSchema,
    TweetListOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_users.schemas import LikeAuthorSchema
from app_users.services import AuthorService
from schemas import ErrorSchema, ErrorSchemasList, SuccessSchema


class TweetService:
    """
    Класс реализует бизнес-логику работы с твиттами.
    """

    def __init__(self):
        """
        Конструктор класса.

        Parameters:
        -----------
        self.service: TweetTransportService
            Связь с сервисом по работе с СУБД.
        self.author_service: AuthorService
            Связь с бизнес-логикой приложения app_users
        """
        self.service = TweetTransportService()
        self.author_service = AuthorService()

    async def get_list(self, api_key: str) -> TweetListOutSchema | ErrorSchema:
        """
        Метод возвращает список твитов пользователя.

        Parameters
        ----------
        api_key: str
            Уникальный идентификатор фронтенда.

        Returns
        -------
        TweetListOutSchema
            Pydantic-схема списка твитов для фронтенда.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        logger.info("запрос твитов для автора...")
        author = await self.author_service.get_author(api_key=api_key)
        tweets = await self.service.get_list(author_id=author.user.id)
        for tweet in tweets:
            logger.info(tweet)
        return TweetListOutSchema(result=True, tweets=tweets)

    async def get_tweet(self, tweet_id: int) -> TweetSchema | ErrorSchema:
        """
        Метод возвращает твит пользователя по идентификатору в СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.

        Returns
        -------
        TweetSchema
            Pydantic-схема твита для фронтенда.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        if tweet := await self.service.get_tweet_by_id(tweet_id):
            return tweet
        return ErrorSchemasList.tweet_not_exists

    async def create_tweet(self, new_tweet: TweetInSchema, api_key: str) -> TweetOutSchema | ErrorSchema:
        """
        Метод добавляет твит автора в СУБД.

        Parameters
        ----------
        new_tweet: TweetInSchema
            Pydantic-схема Входящего от фронтенда твита.
        api_key: str
            Уникальный идентификатор автора от фронтенда.

        Returns
        -------
        TweetOutSchema
            Pydantic-схема вновь созданного твита для фронтенда.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        logger.info("создаём твит: %s", new_tweet.dict())
        if author := await self.author_service.get_author(api_key=api_key):
            attachments = await MediaService.get_many_media(new_tweet.tweet_media_ids)
            created_tweet = await self.service.create_tweet(new_tweet, author.user.id, attachments)
            return TweetOutSchema(result=True, tweet_id=created_tweet.id)
        return ErrorSchemasList.author_not_exists

    async def delete_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema | ErrorSchema:
        """
        Метод удаляет твит автора из СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        api_key: str
            Уникальный идентификатор автора от фронтенда.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        logger.info("удалим твит, id: %s", tweet_id)
        author = await self.author_service.get_author(api_key=api_key)
        if not author:
            return ErrorSchemasList.author_not_exists
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        if not tweet:
            return ErrorSchemasList.tweet_not_exists
        logger.debug(
            "сравнение идентификаторов автора запроса и автора твитта %s <?> %s", author.user.id, tweet.author.id
        )
        if not tweet.author.id == author.user.id:
            return ErrorSchemasList.not_self_tweet_remove
        try:
            return await self.service.delete_tweet(tweet_id=tweet_id, author_id=author.user.id)
        except BaseException as e:
            logger.error("неизвестная ошибка при удалении твита")
            logger.trace(e)
            return ErrorSchema(
                error_type="ERR_TWEET_DELETE",
                error_message="непредвиденная ошибка удаления твита",
            )

    async def add_like_to_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema | ErrorSchema:
        """
        Метод добавляет лайку к твиту.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        api_key: str
            Уникальный идентификатор автора от фронтенда.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        logger.info("поставим лайк на твит...")
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = LikeAuthorSchema(user_id=author.user.id, name=author.user.name)
        if like in tweet.likes:
            response = ErrorSchemasList.double_like
            logger.warning(response)
            return response
        tweet.likes.append(like)
        return await self.service.update_like_in_tweet(tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"])

    async def remove_like_from_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema | ErrorSchema:
        """
        Метод удаляет лайку из твита.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        api_key: str
            Уникальный идентификатор автора от фронтенда.

        Returns
        -------
        SuccessSchema
            Pydantic-схема успешной операции.
        ErrorSchema
            Pydantic-схема ошибки выполнения.
        """
        logger.info("удалим лайк на твит...")
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = LikeAuthorSchema(user_id=author.user.id, name=author.user.name)
        if like not in tweet.likes:
            return ErrorSchemasList.remove_not_exist_like
        tweet.likes.remove(like)
        return await self.service.update_like_in_tweet(tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"])

    async def check_belongs_tweet_to_author(self, tweet_id: int, author_id: int) -> t.Optional[bool]:
        """
        Метод проверяет принадлежность твита конкретному автору.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        author_id: int
            Идентификатор автора в СУБД.

        Returns
        -------
        bool
            True если этот твит принадлежит автору
        """
        tweet: TweetSchema = await self.service.get_tweet_by_id(tweet_id)
        if not tweet.author.id == author_id:
            raise BelongsTweetToAuthorException("Твит не принадлежит автору")
        return True

