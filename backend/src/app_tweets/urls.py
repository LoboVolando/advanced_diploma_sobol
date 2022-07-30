import logging

from fastapi import APIRouter, Depends

from .schemas import (
    MeAuthorOutSchema,
    TweetInSchema,
    TweetOutSchema,
    TweetSchema,
)
from .services import AuthorService, PermissionService, TweetService
from .transport_services import AuthorMockService as AuthorTransportService
from .transport_services import TweetMockService as TweetTransportService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

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
    await permission.get_api_key()
    return await tweet.create_tweet(new_tweet)


@router.get("/api/userinfo", response_model=MeAuthorOutSchema)
@router.get("/api/users/me", response_model=MeAuthorOutSchema)
async def me(
    user: AuthorService = Depends(AuthorTransportService),
    permission: PermissionService = Depends(),
):
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get("/api")
async def echo():
    print("echo")
    return {"echo": "echo"}
