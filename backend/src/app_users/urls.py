"""
urls.py
-------
Модуль реализует эндпоинты приложения app_users.
"""
from fastapi import APIRouter, Depends, status
from loguru import logger

from app_users.schemas import ProfileAuthorOutSchema, RegisterAuthorSchema
from app_users.services import AuthorService, PermissionService
from schemas import SuccessSchema

router = APIRouter()


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(author: RegisterAuthorSchema, service: AuthorService = Depends()) -> dict:
    """Эндпоинт регистрации нового автора.

    Parameters
    ----------
    author: RegisterAuthorSchema
        Pydantic-схема с данными автора, для регистрации.
    service: AuthorService
        Зависимость, реализующая бизнес-логику работы с авторами.

    Returns
    -------
    dict
        Возвращает словарь::

            {
                'result': bool,
                'api-key': str,
                'created': bool,
            }

    Note
    ----
    Не предусмотрен документацией проекта.
    """
    logger.warning("регистрируем нового пользователя...")
    api_key, created = await service.get_or_create_user(name=author.name, password=author.password)
    logger.info(api_key)
    return {"result": "true", "api-key": api_key, "created": created}


@router.get("/api/userinfo", response_model=ProfileAuthorOutSchema, status_code=status.HTTP_200_OK)
@router.get("/api/users/me", response_model=ProfileAuthorOutSchema, status_code=status.HTTP_200_OK)
async def me(
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> ProfileAuthorOutSchema:
    """Эндпоинт возвращает информацию о текущем пользователе.

    Parameters
    ----------
    user: AuthorService
        Зависимость реализует бизнес-логику работы с пользователями.
    permission: PermissionService
        Зависимость реализует бизнес-логику работы с правами.

    Returns
    -------
    ProfileAuthorOutSchema
        pydantic-схема профиля пользователя.
    """
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get("/api/users/{author_id}", status_code=status.HTTP_200_OK, response_model=ProfileAuthorOutSchema)
async def get_author_by_id(
    author_id: int,
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> ProfileAuthorOutSchema:
    """Эндпоинт возвращает автора по идентификатору в базе данных.

    Parameters
    ----------
    author_id: int
        Идентификатор автора для запроса.
    user: AuthorService
        Зависимость реализующая бизнес-логику для работы с пользователями.
    permission: PermissionService
        Зависимость, реализующая логику работы с правами.

    Returns
    -------
    ProfileAuthorOutSchema
        pydantic-схема профиля пользователя.

    """
    await permission.get_api_key()
    logger.info("run api")
    return await user.get_author(author_id=author_id)


@router.post("/api/users/{author_id}/follow", response_model=SuccessSchema, status_code=status.HTTP_200_OK)
async def follow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
) -> SuccessSchema:
    """Эндпоинт добавляет пишущему автору читателей, а читателям - писателя.

    Parameters
    ----------
    author_id: int
        Идентификатор пишущего автора.
    permission: PermissionService
        Зависимость для работы с правами.
    author: AuthorService
        Зависимость, реализующая бизнес-логику работы с авторами.

    Returns
    -------
    SuccessSchema
        Pydantic-схема успешного выполнения.

    Note
    ----
    Идентификатор читающего автора извлекается при помощи зависимости permission.
    """
    api_key = await permission.get_api_key()
    return await author.add_follow(writing_author_id=author_id, api_key=api_key)


@router.delete("/api/users/{author_id}/follow", response_model=SuccessSchema, status_code=status.HTTP_200_OK)
async def unfollow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
) -> SuccessSchema:
    """Эндпоинт удаляет у пишущего автора читателя, а у  читателя - писателя.

    Parameters
    ----------
    author_id: int
        Идентификатор пишущего автора.
    permission: PermissionService
        Зависимость для работы с правами.
    author: AuthorService
        Зависимость, реализующая бизнес-логику работы с авторами.

    Returns
    -------
    SuccessSchema
        Pydantic-схема успешного выполнения.

    Note
    ----
    Идентификатор читающего автора извлекается при помощи зависимости permission.
    """

    api_key = await permission.get_api_key()
    return await author.remove_follow(writing_author_id=author_id, api_key=api_key)
