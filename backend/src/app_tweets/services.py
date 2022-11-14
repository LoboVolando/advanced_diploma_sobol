"""
services.py
-----------

Модуль определяет бизнес-логику приложения app_tweets.
"""
from pydantic import ValidationError

from app_media.services import MediaService
from app_tweets.db_services import TweetDbService as TweetTransportService
from app_tweets.schemas import (
    TweetInSchema,
    TweetListOutSchema,
    TweetModelOutSchema,
    TweetOutSchema,
)
from app_users.schemas import AuthorLikeSchema
from app_users.services import AuthorService
from exceptions import BackendException, ErrorsList
from log_fab import get_logger
from schemas import SuccessSchema

logger = get_logger()


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

    async def get_list(self, api_key: str) -> TweetListOutSchema:
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
        author = await self.author_service.get_author(api_key=api_key)
        tweets = await self.service.get_list(author_id=author.user.id)
        try:
            result = TweetListOutSchema(result=True, tweets=tweets)
        except ValidationError as e:
            logger.exception(event="ошибка преобразования в схему", exc_info=e)
            raise BackendException(**ErrorsList.serialize_error)
        else:
            logger.info(event="успешное преобразование списка твитов в схему", result=result.result, count=len(tweets))
            return result

    async def get_tweet(self, tweet_id: int) -> TweetModelOutSchema:
        """
        Метод возвращает твит пользователя по идентификатору в СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.

        Returns
        -------
        TweetModelOutSchema
            Pydantic-схема модели твита.
        """
        if tweet := await self.service.get_tweet_by_id(tweet_id):
            return TweetModelOutSchema(result=True, tweet=tweet)
        logger.warning(event="запрос твита с несуществующим id", tweet_id=tweet_id)
        raise BackendException(**ErrorsList.tweet_not_exists)

    async def create_tweet(self, new_tweet: TweetInSchema, api_key: str) -> TweetOutSchema:
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
        """
        logger.info(event="творим твит", new_tweet=new_tweet.dict())
        if author := await self.author_service.get_author(api_key=api_key):
            attachments = await MediaService.get_many_media(new_tweet.tweet_media_ids)
            created_tweet = await self.service.create_tweet(new_tweet, author.user.id, attachments)
            try:
                result = TweetOutSchema(result=True, tweet_id=created_tweet.id)
            except ValidationError as e:
                logger.exception(event="ошибка преобразования в схему", exc_info=e)
                raise BackendException(**ErrorsList.serialize_error)
            else:
                logger.info(event="успешное преобразование списка твитов в схему", result=result.result)
                return result
        logger.error(event="попытка создать твит несуществующим автором")
        raise BackendException(**ErrorsList.author_not_exists)

    async def delete_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema:
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
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        if not tweet.author.id == author.user.id:
            logger.error(
                event="сравнение идентификаторов автора запроса и автора твитта %s <?> %s",
                author_id=author.user.id,
                tweet_id=tweet.author.id,
            )
            raise BackendException(**ErrorsList.not_self_tweet_remove)
        return await self.service.delete_tweet(tweet_id=tweet_id, author_id=author.user.id)

    async def add_like_to_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema:
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
        """
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = AuthorLikeSchema(user_id=author.user.id, name=author.user.name)
        if like in tweet.likes:
            logger.error(event="попытка двойного лайка", tweet_id=tweet_id, author_id=author.user.id)
            raise BackendException(**ErrorsList.double_like)
        tweet.likes.append(like.dict())
        result = await self.service.update_like_in_tweet(
            tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"]
        )
        logger.info(event="добавлен лайк", author_id=like.user_id, tweet_id=tweet.id)
        return result

    async def remove_like_from_tweet(self, tweet_id: int, api_key: str) -> SuccessSchema:
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
        """
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = AuthorLikeSchema(user_id=author.user.id, name=author.user.name)
        if like not in tweet.likes:
            logger.error(event="попытка удаления не своего лайка", tweet_id=tweet_id, author_id=author.user.id)
            raise BackendException(**ErrorsList.remove_not_exist_like)
        tweet.likes.remove(like.dict())
        result = await self.service.update_like_in_tweet(
            tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"]
        )
        logger.info(event="удалён лайк", author_id=like.user_id, tweet_id=tweet.id)
        return result
