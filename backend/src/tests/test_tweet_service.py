import typing as t

import pytest
from loguru import logger

from app_tweets.schemas import TweetOutSchema, TweetListOutSchema, TweetInSchema, TweetSchema
from app_tweets.services import TweetService
from app_users.services import AuthorService
from exceptions import BackendException
from schemas import SuccessSchema
from tests.test_user_service import register_fake_users


@pytest.mark.service
@pytest.mark.asyncio
async def test_get_tweet_list(tweet_service, author_service, faker):
    """3 в 1. Тестируется getlist, get_tweet и create_tweet в корутине register_fake_tweets"""
    user_count = 5
    tweet_count = 5
    tweets_ids = []
    api_keys, users, tweets = await register_fake_tweets(user_count=user_count, tweet_count=tweet_count, faker=faker,
                                                         author_service=author_service, tweet_service=tweet_service)
    for api_key, tweet_list in tweets.items():
        left_tweets = set([tweet.tweet_id for tweet in tweet_list])
        temp_list = await tweet_service.get_list(api_key)
        assert isinstance(temp_list, TweetListOutSchema)
        right_tweet_list = [tweet.id for tweet in temp_list.tweets]
        right_tweets = set(right_tweet_list)
        tweets_ids.extend(right_tweets)
        assert left_tweets == right_tweets
    assert len(tweets_ids) == user_count * tweet_count
    for tweet_id in tweets_ids:
        tweet = await tweet_service.get_tweet(tweet_id=tweet_id)
        assert isinstance(tweet, TweetSchema)


@pytest.mark.service
@pytest.mark.asyncio
async def test_add_remove_like_to_tweet(author_service, tweet_service, faker):
    user_count = 5
    tweet_count = 2
    api_keys, users, tweets = await register_fake_tweets(tweet_count=tweet_count, user_count=user_count, faker=faker,
                                                         author_service=author_service, tweet_service=tweet_service)
    source_user_id, tweet_ids = await add_remove_like("add", api_keys, tweets, author_service, tweet_service)
    for tweet_id in tweet_ids:
        tweet = await tweet_service.get_tweet(tweet_id=tweet_id)
        assert len(tweet.likes) == 1
        for like in tweet.likes:
            assert like.user_id == source_user_id
    source_user_id, tweet_ids = await add_remove_like("remove", api_keys, tweets, author_service, tweet_service)
    logger.info(f"source_user_id: {source_user_id}")
    for tweet_id in tweet_ids:
        tweet = await tweet_service.get_tweet(tweet_id=tweet_id)
        logger.info(f"tweet: {tweet}")
        for like in tweet.likes:
            assert len(tweet.likes) == 0


@pytest.mark.service
@pytest.mark.asyncio
async def test_tweet_delete(author_service, tweet_service, faker):
    user_count = 5
    tweet_count = 2
    api_keys, users, tweets = await register_fake_tweets(tweet_count=tweet_count, user_count=user_count, faker=faker,
                                                         author_service=author_service, tweet_service=tweet_service)
    ids = []
    for api_key, tweet_list in tweets.items():
        for t in tweet_list:
            logger.info(t)
            ids.append((api_key, t.tweet_id))
    assert len(ids) == user_count * tweet_count
    with pytest.raises(BackendException):
        for tweet in ids:
            result = await tweet_service.delete_tweet(tweet_id=tweet[1], api_key='0')
    for tweet in ids:
        delete_result = await tweet_service.delete_tweet(tweet_id=tweet[1], api_key=tweet[0])
        assert isinstance(delete_result, SuccessSchema)
        with pytest.raises(BackendException):
            await tweet_service.get_tweet(tweet[1])


async def register_fake_tweets(user_count: int, tweet_count: int, faker,
                               author_service: AuthorService, tweet_service: TweetService):
    api_keys, users = await register_fake_users(count=user_count, author_service=author_service, faker=faker)
    assert len(users) == len(api_keys) == user_count
    tweets = dict()
    for key in api_keys:
        tweets[key] = list()
        for _ in range(tweet_count):
            new_tweet = TweetInSchema(tweet_data=faker.text(max_nb_chars=100), tweet_media_ids=[], attachments=[])
            created_tweet = await tweet_service.create_tweet(new_tweet=new_tweet, api_key=key)
            assert isinstance(created_tweet, TweetOutSchema)
            tweets[key].append(created_tweet)
    return api_keys, users, tweets


async def add_remove_like(mode: str, api_keys: t.List[str], tweets: dict, author_service: AuthorService,
                          tweet_service: TweetService) -> tuple:
    tweet_ids = []
    source_key = api_keys[0]
    source_user = await author_service.get_author(api_key=source_key)
    source_user_id = source_user.user.id
    for target_key in api_keys[1:]:
        target_tweets = tweets[target_key]
        for tweet in target_tweets:
            tweet_ids.append(tweet.tweet_id)
            if mode == 'add':
                result = await tweet_service.add_like_to_tweet(tweet_id=tweet.tweet_id, api_key=source_key)
            else:
                result = await tweet_service.remove_like_from_tweet(tweet_id=tweet.tweet_id, api_key=source_key)
            assert isinstance(result, SuccessSchema)
            assert result.result is True
    return source_user_id, tweet_ids
