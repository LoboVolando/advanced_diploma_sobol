import logging

from fastapi import APIRouter, Depends

from app_tweets.schemas import (
    SuccessSchema,
    TweetInSchema,
    TweetListOutSchema,
    TweetOutSchema,
)
from app_tweets.services import TweetService
from app_users.services import PermissionService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

router = APIRouter()


@router.get("/api/tweets", response_model=TweetListOutSchema)
async def get_tweets_list(
    permission: PermissionService = Depends(), tweet: TweetService = Depends()
):
    api_key = await permission.get_api_key()
    return await tweet.get_list(api_key)


@router.post("/api/tweets", response_model=TweetOutSchema)
async def create_tweet(
    new_tweet: TweetInSchema,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> TweetOutSchema:
    api_key = await permission.get_api_key()
    return await tweet.create_tweet(new_tweet, api_key)


@router.delete("/api/tweets/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    logger.info("run delete api: %s", "/api/tweets/{tweet_id}")
    api_key = await permission.get_api_key()
    return await tweet.delete_tweet(tweet_id=tweet_id, api_key=api_key)


@router.post("/api/tweets/{tweet_id}/likes", response_model=SuccessSchema)
async def add_like_to_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    api_key = await permission.get_api_key()
    return await tweet.add_like_to_tweet(tweet_id=tweet_id, api_key=api_key)


@router.delete("/api/tweets/{tweet_id}/likes", response_model=SuccessSchema)
async def remove_like_from_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    api_key = await permission.get_api_key()
    return await tweet.remove_like_from_tweet(
        tweet_id=tweet_id, api_key=api_key
    )
