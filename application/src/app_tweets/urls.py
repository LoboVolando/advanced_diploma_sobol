import logging

from fastapi import APIRouter, Depends

from .schemas import TweetSchema, TweetInSchema, TweetOutSchema, MeAuthorOutSchema
from .services import TweetService, PermissionService, AuthorService
from .transport_services import TweetMockService as TweetTransportService
from .transport_services import AuthorMockService as AuthorTransportService

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO', handlers=[logging.StreamHandler()])

router = APIRouter()


@router.get("/api/tweets", response_model=list[TweetSchema])
async def get_tweets_list(
        permission: PermissionService = Depends(),
        tweet: TweetService = Depends(TweetTransportService),
) -> list[TweetSchema]:
    await permission.get_api_key()
    return await tweet.get_list()


@router.post("/api/tweets", response_model=TweetOutSchema)
async def create_tweet(
        new_tweet: TweetInSchema,
        permission: PermissionService = Depends(),
        tweet: TweetService = Depends(TweetTransportService),
) -> TweetOutSchema:
    api_key = await permission.get_api_key()
    return await tweet.create_tweet(new_tweet)


@router.get("/api/users/me", response_model=MeAuthorOutSchema)
async def me(
        user: AuthorService = Depends(AuthorTransportService),
        permission: PermissionService = Depends()):
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get("/api")
async def echo():
    print('echo')
    return {"echo": "echo"}


@router.get("/api/userinfo")
async def user_info(permission: PermissionService = Depends()):
    # await permission.get_api_key()
    return {"result": "true", "user": {"id": 1, "name": "john doe"}}
