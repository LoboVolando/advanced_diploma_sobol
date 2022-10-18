import pytest
from fastapi import status
from httpx import AsyncClient
from loguru import logger

from app_tweets.schemas import *
from exceptions import BackendException


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_tweet_list_api(get_tweet_schemas_list, get_app, faker):
    app = await get_app
    author_list, tweet_list = await get_tweet_schemas_list
    for author in author_list:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with pytest.raises(BackendException):
                await ac.get('/api/tweets', headers={"api-key": faker.pystr(10)})
            response = await ac.get('/api/tweets', headers={"api-key": author.api_key})
            assert response.status_code == status.HTTP_200_OK
            response_dict = response.json()
            assert isinstance(TweetListOutSchema(**response_dict), TweetListOutSchema)
            assert set(response_dict.keys()) == {"result", "tweets"}
    logger.info("complete")


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_tweet_api(get_authors_api_key_list, get_app, faker):
    app = await get_app
    api_key_list = await get_authors_api_key_list
    for api_key in api_key_list:
        data = dict(tweet_data=faker.text(200), tweet_media_ids=[])
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with pytest.raises(BackendException):
                await ac.post('/api/tweets', headers={"api-key": faker.pystr(10)}, json=data)
            response = await ac.post('/api/tweets', headers={"api-key": api_key}, json=data)
            assert response.status_code == status.HTTP_201_CREATED
            response_dict = response.json()
            assert set(response_dict.keys()) == {"result", "tweet_id"}
            assert response_dict["result"] is True
            assert response_dict["tweet_id"] > 0
    logger.info("complete")


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_tweet_api(get_tweet_schemas_list, get_app, faker):
    app = await get_app
    author_list, tweet_list = await get_tweet_schemas_list
    for author in author_list:
        for tweet in tweet_list:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                with pytest.raises(BackendException):
                    await ac.get(f'/api/tweets/{tweet.id}', headers={"api-key": faker.pystr(10)})
                response = await ac.get(f'/api/tweets/{tweet.id}', headers={"api-key": author.api_key})
                assert response.status_code == status.HTTP_200_OK
                response_dict = response.json()
                assert set(response_dict.keys()) == {"result", "tweet"}
                assert response_dict["result"] is True
    logger.info("complete")


@pytest.mark.api
@pytest.mark.asyncio
async def test_delete_tweet_api(get_tweet_schemas_list, get_app, faker):
    app = await get_app
    author_list, tweet_list = await get_tweet_schemas_list
    author_dict = {author.id: author for author in author_list}
    for tweet in tweet_list:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with pytest.raises(BackendException):
                await ac.delete(f'/api/tweets/{tweet.id}', headers={"api-key": faker.pystr(10)})
            response = await ac.delete(f'/api/tweets/{tweet.id}',
                                       headers={"api-key": author_dict.get(tweet.author_id).api_key})
            response_json = response.json()
            assert response.status_code == status.HTTP_200_OK
            assert set(response_json.keys()) == {"result"}
            assert response_json["result"] is True
    logger.info("complete")
