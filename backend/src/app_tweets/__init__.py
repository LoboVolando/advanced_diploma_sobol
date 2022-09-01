"""
app_tweets.py
==============
приложение для обмена сообщениями
"""
from fastapi import APIRouter

from app_tweets.urls import router as tweets_router

router = APIRouter()
router.include_router(tweets_router)
