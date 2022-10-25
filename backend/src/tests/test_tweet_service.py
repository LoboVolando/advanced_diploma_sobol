import typing as t

import pytest
from loguru import logger

from app_tweets.schemas import (
    AuthorLikeSchema,
    TweetInSchema,
    TweetModelOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_tweets.services import TweetService
from app_users.services import AuthorService
from exceptions import BackendException
from schemas import SuccessSchema


@pytest.mark.service
@pytest.mark.asyncio
async def test_get_tweet_list(get_tweet_schemas_list, tweet_service, faker):
    authors_list, tweet_list = await get_tweet_schemas_list
    tweet_dict = {tweet.id: tweet for tweet in tweet_list}
    with pytest.raises(BackendException):
        await tweet_service.get_list(faker.pystr(10))

    for author in authors_list:
        tweets = await tweet_service.get_list(author.api_key)
        assert set(tweets.dict().keys()) == {"result", "tweets"}
        assert tweets.result is True
        for tweet in tweets.tweets:
            assert set(tweet.dict().keys()) == {"id", "content", "attachments", "author", "likes"}
            assert set(tweet.author.dict()) == {"id", "name"}
            assert TweetSchema(**tweet_dict.get(tweet.id).dict()) == tweet


@pytest.mark.service
@pytest.mark.asyncio
async def test_tweet_by_id(get_tweet_schemas_list, tweet_service, faker):
    """недокументированое апи"""
    authors_list, tweet_list = await get_tweet_schemas_list
    for tweet_item in tweet_list:
        tweet = await tweet_service.get_tweet(tweet_item.id)
        assert isinstance(tweet, TweetModelOutSchema)


@pytest.mark.service
@pytest.mark.asyncio
async def test_create_tweet(get_authors_schemas_list, tweet_service, faker):
    authors_list = await get_authors_schemas_list
    for author in authors_list:
        tweet = await tweet_service.create_tweet(
            TweetInSchema(tweet_data=faker.text(200), tweet_media_ids=[]), author.api_key
        )
        assert isinstance(tweet, TweetOutSchema)
        assert set(tweet.dict().keys()) == {"result", "tweet_id"}


@pytest.mark.service
@pytest.mark.asyncio
async def test_add_remove_like_to_tweet(get_tweet_schemas_list, tweet_service, faker):
    authors_list, tweet_list = await get_tweet_schemas_list
    source_author = authors_list[0]
    authors_list = authors_list[1:]
    tweets = await tweet_service.get_list(source_author.api_key)
    for tweet in tweets.tweets:
        for author in authors_list:
            result = await tweet_service.add_like_to_tweet(tweet.id, author.api_key)
            assert isinstance(result, SuccessSchema)
            assert result.result is True
            verify_tweet = await tweet_service.get_tweet(tweet.id)
            assert AuthorLikeSchema(user_id=author.id, name=author.name).dict() in verify_tweet.tweet.likes
            result = await tweet_service.remove_like_from_tweet(tweet.id, author.api_key)
            assert isinstance(result, SuccessSchema)
            assert result.result is True
            verify_tweet = await tweet_service.get_tweet(tweet.id)
            assert AuthorLikeSchema(user_id=author.id, name=author.name).dict() not in verify_tweet.tweet.likes


@pytest.mark.service
@pytest.mark.asyncio
async def test_tweet_delete(get_tweet_schemas_list, tweet_service, faker):
    authors_list, tweet_list = await get_tweet_schemas_list
    for author in authors_list:
        tweets = await tweet_service.get_list(author.api_key)
        for tweet in tweets.tweets:
            result = await tweet_service.delete_tweet(tweet_id=tweet.id, api_key=author.api_key)
            assert isinstance(result, SuccessSchema)
            check_tweet = await tweet_service.get_tweet(tweet.id)
            assert check_tweet.tweet.soft_delete is True
            assert check_tweet.tweet.id == tweet.id
