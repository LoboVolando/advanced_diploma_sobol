from fastapi import APIRouter, Depends

from .schemas import TweetBaseSchema
from .services import TweetService
from .transport_services import TweetMockService as TweetTransportService

router = APIRouter()


@router.get("/api/tweets", response_model=list[TweetBaseSchema])
async def tweet_list(
        tweet: TweetService = Depends(TweetTransportService),
) -> list[TweetBaseSchema]:
    return tweet.get_list()
