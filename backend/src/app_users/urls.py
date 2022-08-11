import logging

from fastapi import APIRouter, Depends

from app_users.exceptions import PasswordIncorrect
from app_users.schemas import ErrorSchema, RegisterAuthorSchema, SuccessSchema
from app_users.services import AuthorService, PermissionService

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", handlers=[logging.StreamHandler()])

router = APIRouter()


@router.post("/api/register")
async def register(
    author: RegisterAuthorSchema, service: AuthorService = Depends()
):
    logger.warning("регистрируем нового пользователя...")
    try:
        api_key, created = await service.get_or_create_user(
            name=author.name, password=author.password
        )
        logger.info(api_key)
        return {"result": "true", "api-key": api_key, "created": created}
    except PasswordIncorrect:
        ErrorSchema(
            error_type="INCORRECT_PASSWROR",
            error_message=f"неверный пароль для: {author.name}",
        ).dict()


@router.get("/api/userinfo")
@router.get("/api/users/me")
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
    return await user.get_author(author_id=author_id)


@router.post("/api/users/{author_id}/follow")
async def follow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
) -> SuccessSchema | ErrorSchema:
    api_key = await permission.get_api_key()
    return await author.add_follow(
        writing_author_id=author_id, api_key=api_key
    )


@router.delete("/api/users/{author_id}/follow", response_model=SuccessSchema)
async def unfollow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
):
    api_key = await permission.get_api_key()
    return await author.remove_follow(
        writing_author_id=author_id, api_key=api_key
    )
