import hashlib
import shutil
import typing as t
from pathlib import Path

from fastapi import UploadFile
from loguru import logger

from app_tweets.db_services import MediaDbService as MediaTransportService
from app_tweets.db_services import TweetDbService as TweetTransportService
from app_tweets.exceptions import BelongsTweetToAuthorException
from app_tweets.schemas import (
    MediaOutSchema,
    TweetInSchema,
    TweetListOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_users.schemas import LikeAuthorSchema
from app_users.services import AuthorService
from settings import settings

from schemas import ErrorSchemasList, ErrorSchema


class TweetService:
    """
    бизнес-логика работы с твиттами
    """

    def __init__(self):
        self.service = TweetTransportService()
        self.author_service = AuthorService()

    async def get_list(self, api_key: str) -> TweetListOutSchema:
        logger.info("запрос твитов для автора...")
        author = await self.author_service.get_author(api_key=api_key)
        tweets = await self.service.get_list(author_id=author.user.id)
        for tweet in tweets:
            logger.info(tweet)
        return TweetListOutSchema(result=True, tweets=tweets)

    async def get_tweet(self, tweet_id: int) -> TweetSchema | ErrorSchema:
        if tweet := await self.service.get_tweet_by_id(tweet_id):
            return tweet
        return self.make_no_tweet_response(tweet_id)

    async def create_tweet(self, new_tweet: TweetInSchema, api_key: str) -> TweetOutSchema:
        """Логика добавления твита"""
        logger.info("создаём твит: %s", new_tweet.dict())
        if author := await self.author_service.get_author(api_key=api_key):
            attachments = await MediaService.get_many_media(new_tweet.tweet_media_ids)
            created_tweet = await self.service.create_tweet(new_tweet, author.user.id, attachments)
            return TweetOutSchema(result=True, tweet_id=created_tweet.id)
        return ErrorSchemasList.author_not_exists

    async def delete_tweet(self, tweet_id: int, api_key: str):
        """сервис удаления твита по id"""
        logger.info("удалим твит, id: %s", tweet_id)
        author = await self.author_service.get_author(api_key=api_key)
        if not author:
            return ErrorSchemasList.author_not_exists
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        if not tweet:
            return self.make_no_tweet_response(tweet_id=tweet_id)
        logger.debug(
            "сравнение идентификаторов автора запроса и автора твитта %s <?> %s", author.user.id, tweet.author.id
        )
        if not tweet.author.id == author.user.id:
            return self.make_not_self_tweet_remove_response(tweet, author)
        try:
            return await self.service.delete_tweet(tweet_id=tweet_id, author_id=author.user.id)
        except Exception as e:
            logger.error("неизвестная ошибка при удалении твита")
            logger.trace(e)
            return ErrorSchema(
                error_type="ERR_TWEET_DELETE",
                error_message="непредвиденная ошибка удаления твита",
            )

    async def add_like_to_tweet(self, tweet_id: int, api_key: str):
        """бизнес-логика добавления лайка"""
        logger.info("поставим лайк на твит...")
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = LikeAuthorSchema(user_id=author.user.id, name=author.user.name)
        if like in tweet.likes:
            response = self.make_double_like_response(author_id=author.user.id, tweet_id=tweet_id)
            logger.info(response)
            return response
        tweet.likes.append(like)
        return await self.service.add_like_to_tweet(tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"])

    async def remove_like_from_tweet(self, tweet_id: int, api_key: str):
        """бизнес-логика добавления лайка"""
        logger.info("удалим лайк на твит...")
        author = await self.author_service.get_author(api_key=api_key)
        tweet = await self.service.get_tweet_by_id(tweet_id=tweet_id)
        like = LikeAuthorSchema(user_id=author.user.id, name=author.user.name)
        if like not in tweet.likes:
            return self.make_remove_not_exist_like(author_id=author.user.id, tweet_id=tweet_id)
        tweet.likes.remove(like)
        return await self.service.add_like_to_tweet(tweet_id=tweet_id, likes=tweet.dict(include={"likes"})["likes"])

    async def check_belongs_tweet_to_author(self, tweet_id: int, author_id: int) -> t.Optional[bool]:
        """логика проверки принадлежности твита конкретному автору"""
        tweet: TweetSchema = await self.service.get_tweet_by_id(tweet_id)
        if not tweet.author.id == author_id:
            raise BelongsTweetToAuthorException("Твит не принадлежит автору")
        return True

    def make_no_tweet_response(self, tweet_id):
        logger.error(f"твит не существует {tweet_id}")
        return ErrorSchema(
            error_type="TWEET_NOT_EXIST",
            error_message=f"операции над несуществующим твитом {tweet_id} невозможны",
        )

    def make_not_self_tweet_remove_response(self, tweet, author):
        logger.error(f"попытка удаления не своего твита")
        return ErrorSchema(
            error_type="TWEET_NOT_BELONGS_TO_AUTHOR",
            error_message=f"{author.user.name}, нельзя удалять чужие ({tweet.author.name}) твиты, редиска",
        )

    def make_double_like_response(self, author_id: int, tweet_id: int):
        logger.error(f"попытка лайкнуться дважды")
        return ErrorSchema(
            error_type="DOUBLE_LIKE_ERROR",
            error_message=f"автор: {author_id} пытался закинуть несколько лайков на твит {tweet_id}",
        )

    def make_remove_not_exist_like(self, author_id: int, tweet_id: int):
        logger.error(f"попытка удалить несуществующий лайк")
        return ErrorSchema(
            error_type="REMOVE_NOT_EXITS_LIKE",
            error_message=f"автор: {author_id} пытался удалить несуществующий лайк на твит {tweet_id}",
        )


class MediaService:
    @staticmethod
    async def get_or_create_media(file: UploadFile):

        bytez = await file.read()
        hash = hashlib.sha256(bytez).hexdigest()
        logger.warning(hash)
        if media := await MediaTransportService.get_media(hash=hash):
            return MediaOutSchema(media_id=media.id)
        MediaService.write_media_to_static_folder(file)
        if media := await MediaTransportService.create_media(hash=hash, file_name=file.filename):
            return MediaOutSchema(media_id=media.id)
        return MediaService.make_error_response()

    @staticmethod
    def write_media_to_static_folder(file: UploadFile):
        path = Path(settings.media_root) / file.filename
        with open(path, "wb") as fl:
            file.file.seek(0)
            logger.info(f"запишем картинку в файл: {str(path)}")
            shutil.copyfileobj(file.file, fl)
            file.file.close()
        for file in Path(settings.media_root).glob("*.*"):
            logger.info(f"{file.absolute()}")

    @staticmethod
    async def get_many_media(ids: t.List[int]) -> t.Optional[t.List[str]]:
        """получим список картинок по id"""
        logger.info(f"запросим медиа по идентификаторам: {ids}")
        if attachments := await MediaTransportService.get_many_media(ids):
            return attachments
        return list()

    @staticmethod
    def make_error_response():
        return ErrorSchema(
            error_type="MEDIA_IMPORT_ERROR",
            error_message="непредвиденная ошибка сохранения картинки ",
        )
