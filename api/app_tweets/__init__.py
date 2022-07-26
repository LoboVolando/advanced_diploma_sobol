from fastapi import APIRouter

from api.app_tweets.urls import router as tweets_router

router = APIRouter()
router.include_router(tweets_router)
