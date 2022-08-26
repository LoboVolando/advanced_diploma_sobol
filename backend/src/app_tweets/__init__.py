from app_tweets.urls import router as tweets_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(tweets_router)
