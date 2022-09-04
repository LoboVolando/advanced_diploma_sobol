"""
app_users
---------

Приложение для работы с пользователями системы
"""
from fastapi import APIRouter

from app_users.urls import router as users_router

router = APIRouter()
router.include_router(users_router)
