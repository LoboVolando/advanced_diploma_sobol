import logging

from fastapi import APIRouter, Depends

from .schemas import (
    ProfileAuthorOutSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetSchema,
    TweetListOutSchema,
)
from .services import AuthorService, PermissionService, TweetService

# , ,
# from .transport_services import AuthorMockService as AuthorTransportService
# from .transport_services import TweetMockService as TweetTransportService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

router = APIRouter()


@router.get("/api/tweets", response_model=TweetListOutSchema)
async def get_tweets_list(
        permission: PermissionService = Depends(),
        tweet: TweetService = Depends(),
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


@router.get("/api/userinfo", response_model=ProfileAuthorOutSchema)
@router.get("/api/users/me", response_model=ProfileAuthorOutSchema)
async def me(user: AuthorService = Depends(),
             permission: PermissionService = Depends(),
             ):
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get('/api/users/{author_id}')
async def get_author_by_id(author_id: int,
                           user: AuthorService = Depends(),
                           permission: PermissionService = Depends(),
                           ):
    await permission.get_api_key()
    logger.info('run api')
    return await user.get_author_by_id(author_id)

# @router.get("/api")
# async def echo():
#     print("echo")
#     return {"echo": "echo"}
