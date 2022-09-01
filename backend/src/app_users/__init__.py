from fastapi import APIRouter

from app_users.urls import router as users_router

router = APIRouter()
router.include_router(users_router)
