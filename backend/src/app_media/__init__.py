"""
app_media.py
==============
приложение для работы с media ресурсами
"""
from fastapi import APIRouter

from app_media.urls import router as media_router

router = APIRouter()
router.include_router(media_router)
