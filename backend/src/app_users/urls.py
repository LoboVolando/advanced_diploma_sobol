import logging

from fastapi import APIRouter, Depends

from ..app_users.schemas import ProfileAuthorOutSchema, SuccessSchema
from ..app_users.services import AuthorService, PermissionService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

router = APIRouter()


@router.get("/api/userinfo", response_model=ProfileAuthorOutSchema)
@router.get("/api/users/me", response_model=ProfileAuthorOutSchema)
async def me(
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
):
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get("/api/users/{author_id}", response_model=SuccessSchema)
async def get_author_by_id(
    author_id: int,
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
):
    await permission.get_api_key()
    logger.info("run api")
    return await user.get_author_by_id(author_id)


@router.post("/api/users/{author_id}/follow", response_model=SuccessSchema)
async def follow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
):
    api_key = await permission.get_api_key()
    return await author.add_follow(follow_author_id=author_id, api_key=api_key)


@router.delete("/api/users/{author_id}/follow", response_model=SuccessSchema)
async def unfollow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
):
    api_key = await permission.get_api_key()
    return await author.remove_follow(
        follow_author_id=author_id, api_key=api_key
    )
