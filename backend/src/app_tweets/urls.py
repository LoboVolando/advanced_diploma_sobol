from app_tweets.schemas import TweetInSchema, TweetListOutSchema, TweetOutSchema
from app_tweets.services import MediaService, TweetService
from app_users.services import PermissionService
from fastapi import APIRouter, Depends, Header, UploadFile
from loguru import logger

router = APIRouter()


@router.get("/api/tweets", response_model=TweetListOutSchema)
async def get_tweets_list(permission: PermissionService = Depends(), tweet: TweetService = Depends()):
    api_key = await permission.get_api_key()
    return await tweet.get_list(api_key)


@router.post("/api/tweets")
async def create_tweet(
    new_tweet: TweetInSchema,
    # api_key: str = Header(default='FfF1ZDzlVERHLSTXvb75sYGnPHQKMNWjASCxX2P8Gu06TcwBDJNUIgKIB4dyaC9M'),
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> TweetOutSchema:
    api_key = await permission.get_api_key()
    return await tweet.create_tweet(new_tweet, api_key)


@router.get("/api/tweets/{tweet_id}")
async def get_tweet(
    tweet_id: int,
    tweet: TweetService = Depends(),
):
    logger.info("получим твит по id: %s", tweet_id)
    return await tweet.get_tweet(tweet_id=tweet_id)


@router.delete("/api/tweets/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    logger.info("run delete api: %s", "/api/tweets/{tweet_id}")
    api_key = await permission.get_api_key()
    return await tweet.delete_tweet(tweet_id=tweet_id, api_key=api_key)


@router.post("/api/tweets/{tweet_id}/likes")
async def add_like_to_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    api_key = await permission.get_api_key()
    return await tweet.add_like_to_tweet(tweet_id=tweet_id, api_key=api_key)


@router.delete("/api/tweets/{tweet_id}/likes")
async def remove_like_from_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
):
    api_key = await permission.get_api_key()
    return await tweet.remove_like_from_tweet(tweet_id=tweet_id, api_key=api_key)


@router.post("/api/medias")
async def medias(file: UploadFile):
    if result := await MediaService.get_or_create_media(file):
        return result
