import typing as t

from app_tweets.mok_services import TweetMockService
from loguru import logger
from sqlalchemy import select, update

from db import redis, session

from .models import Media, Tweet
from .schemas import (
    MediaOrmSchema,
    SuccessSchema,
    TweetInSchema,
    TweetSchema,
)


class TweetDbService(TweetMockService):
    async def get_list(self, author_id: int) -> t.Optional[t.List[TweetSchema]]:
        query = select(Tweet).filter_by(author_id=author_id, soft_delete=False)
        async with session() as async_session:
            async with async_session.begin():
                if query_set := await async_session.execute(query):
                    return [TweetSchema.from_orm(item) for item in query_set.scalars()]

    async def create_tweet(
        self,
        new_tweet: TweetInSchema,
        author_id: int,
        attachments: t.List[str],
    ) -> Tweet:
        """создаём твит"""

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

    async def get_tweet_by_id(self, tweet_id: int) -> TweetSchema:
        """запрос в БД по ID"""
        logger.info("запрос твитта по ИД, ключу или имени")
        query = select(Tweet).filter_by(id=tweet_id, soft_delete=False)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                result = qs.scalars().first()
                if result:
                    return TweetSchema.from_orm(result)

    async def delete_tweet(self, tweet_id: int, author_id: int):
        """реализация удаления твита"""
        logger.info("удаляем твит из постгрес")
        query = update(Tweet).filter_by(id=tweet_id, author_id=author_id).values(soft_delete=True)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
                return SuccessSchema()

    async def add_like_to_tweet(self, tweet_id: int, likes: dict) -> SuccessSchema:
        """сервис добавления лайка к твиту"""
        query = update(Tweet).where(Tweet.id == tweet_id).values(likes=likes)
        async with session() as async_session:
            async with async_session.begin():
                await async_session.execute(query)
                await async_session.commit()
        return SuccessSchema()


class MediaDbService:
    @staticmethod
    async def get_media(media_id: int = None, hash: str = None):
        logger.info("запрос медиа ресурса...")
        if hash:
            query = select(Media).filter_by(hash=hash)
        elif media_id:
            query = select(Media).filter_by(id=media_id)
        else:
            return
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().first():
                    return MediaOrmSchema.from_orm(result)

    @staticmethod
    async def create_media(hash: str, file_name: str) -> t.Optional[MediaOrmSchema]:
        media = Media(hash=hash, link="static/" + file_name)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(media)
                await async_session.commit()
                return MediaOrmSchema.from_orm(media)

    @staticmethod
    async def get_many_media(ids: t.List[int]):
        query = select(Media.link).filter(Media.id.in_(ids))
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().all():
                    return result
