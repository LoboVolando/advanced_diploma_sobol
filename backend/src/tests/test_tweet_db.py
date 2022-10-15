import pytest
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import select

from app import app
from app_tweets.models import Tweet
from app_tweets.schemas import TweetInSchema, TweetOutSchema, TweetSchema
from tests.test_media_service import create_many_medias
from tests.test_user_service import register_fake_users

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_tweet(author_service, tweet_db_service, faker):
    """тест записи твита в базу."""
    users_count = 5
    api_keys, users = await register_fake_users(users_count, author_service, faker)
    assert len(users) == users_count
    new_tweet = TweetInSchema(tweet_data='hello')
    for user in users:
        attachements = await create_many_medias(count=2)
        attachements = [attach.media_id for attach in attachements]
        logger.warning(f"attachements: {attachements}")
        tweet = await tweet_db_service.create_tweet(new_tweet=new_tweet, author_id=user.user.id,
                                                    attachments=attachements)
        assert isinstance(tweet, TweetOutSchema)
        assert tweet.result is True
        assert tweet.tweet_id > 0


@pytest.mark.asyncio
async def test_get_tweet_by_id(simple_session, tweet_db_service):
    """тест получение твита по ид"""
    max_tweet_count = 10
    session = await simple_session
    ids = await get_tweet_list(count=max_tweet_count, session=session)
    logger.info(f"ids: {ids}")
    for tweet in ids:
        logger.info(f"selected {tweet}")
        selected_tweet = await tweet_db_service.get_tweet_by_id(tweet_id=tweet[0])
        assert isinstance(selected_tweet, TweetSchema)
        logger.info(f"tweet: {selected_tweet}")


@pytest.mark.asyncio
async def test_get_tweet_list_by_author_id(simple_session, tweet_db_service):
    """тестируем получения списка твитов для автора"""
    max_tweet_count = 10
    session = await simple_session
    query = select(Tweet.author_id).distinct().limit(max_tweet_count)
    ids = list()
    async with session() as async_session:
        async with async_session.begin():
            if query_set := await async_session.execute(query):
                [ids.append(item[0]) for item in query_set]
    assert len(ids) > 0
    assert len(ids) <= max_tweet_count
    logger.info(f'authors_id: {ids}')
    for author_id in ids:
        tweets = await tweet_db_service.get_list(author_id=author_id)
        logger.info(tweets)
        assert len(tweets) > 0
        assert isinstance(tweets[0], TweetSchema)


@pytest.mark.asyncio
async def test_update_likes_for_tweet(simple_session, tweet_db_service, author_service, faker):
    """тест гбновления лайков"""
    users_count = 10
    tweet_count = 10
    session = await simple_session
    tweets = await get_tweet_list(count=tweet_count, session=session)
    api_keys, users = await register_fake_users(count=users_count, author_service=author_service, faker=faker)
    assert len(users) == users_count
    logger.info(f"register {len(users)} fake users")
    likes = [dict(user_id=user.user.id, name=user.user.name) for user in users]
    logger.info(f"create {len(likes)} likes")
    for tweet in tweets:
        await tweet_db_service.update_like_in_tweet(tweet_id=tweet[0], likes=likes)
    logger.info(f"update likes tweets")
    for tweet in tweets:
        selected_tweet = await tweet_db_service.get_tweet_by_id(tweet_id=tweet[0])
        logger.debug(f'likes: {selected_tweet.likes}')
        assert selected_tweet.likes == likes
    logger.info(f"verify likes in tweets")


@pytest.mark.asyncio
async def test_delete_tweet(simple_session, tweet_db_service):
    tweet_count = 10
    session = await simple_session
    tweets = await get_tweet_list(count=tweet_count, session=session)
    logger.info(f"tweets: {tweets}")
    for tweet in tweets:
        await tweet_db_service.delete_tweet(tweet_id=tweet[0], author_id=tweet[3])
    logger.info(f"delete tweets")
    for tweet in tweets:
        query = select(Tweet).filter_by(id=tweet[0], soft_delete=True, author_id=tweet[3])
        async with session() as async_session:
            async with async_session.begin():
                if query_set := await async_session.execute(query):
                    result = query_set.scalars().first()
                    assert result.id == tweet[0]
                    assert result.soft_delete is True
                    logger.debug(f"{dir(result)}")

    logger.info(f"delete tweets")


async def get_tweet_list(count: int, session):
    """функция получает некоторое количество твитов"""
    query = select(Tweet.id, Tweet.content, Tweet.soft_delete, Tweet.author_id).filter_by(soft_delete=False).limit(count)
    async with session() as async_session:
        async with async_session.begin():
            if query_set := await async_session.execute(query):
                result = list(query_set)
                logger.info(f"qs: {result}")
                assert len(result) > 0
                assert len(result) <= count
                return result

