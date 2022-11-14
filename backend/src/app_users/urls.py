"""
urls.py
-------
Модуль реализует эндпоинты приложения app_users.

"""
import structlog
from fastapi import APIRouter, Depends, Request, status

from app_users.schemas import AuthorProfileApiSchema, AuthorRegisterSchema
from app_users.services import AuthorService, PermissionService
from log_fab import make_context
from schemas import SuccessSchema

router = APIRouter()

logger = structlog.get_logger()


@router.post("/api/register", status_code=status.HTTP_201_CREATED, tags=["users"])
async def register(request: Request, author: AuthorRegisterSchema, service: AuthorService = Depends()) -> dict:
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
    make_context(request)
    api_key, created = await service.get_or_create_user(name=author.name, password=author.password)
    result = {"result": True, "api-key": api_key, "created": created}
    logger.info("эндпоинт завершен", result=result)
    return result


@router.get("/api/userinfo", response_model=AuthorProfileApiSchema, status_code=status.HTTP_200_OK, tags=["users"])
@router.get("/api/users/me", response_model=AuthorProfileApiSchema, status_code=status.HTTP_200_OK, tags=["users"])
async def me(
    request: Request,
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> AuthorProfileApiSchema:
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
    make_context(request)
    api_key = await permission.get_api_key()
    result = await user.me(api_key)
    logger.info("эндпоинт завершен", result=result.dict())
    return result


@router.get(
    "/api/users/{author_id}", status_code=status.HTTP_200_OK, response_model=AuthorProfileApiSchema, tags=["users"]
)
async def get_author_by_id(
    request: Request,
    author_id: int,
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> AuthorProfileApiSchema:
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
    make_context(request)
    await permission.get_api_key()
    result = await user.get_author(author_id=author_id)
    logger.info("эндпоинт завершен", result=result.dict())
    return result


@router.post(
    "/api/users/{author_id}/follow", response_model=SuccessSchema, status_code=status.HTTP_200_OK, tags=["users"]
)
async def follow_author(
    request: Request,
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
    make_context(request)
    api_key = await permission.get_api_key()
    result = await author.add_follow(writing_author_id=author_id, api_key=api_key)
    logger.info("эндпоинт завершен", result=result.dict())
    return result


@router.delete(
    "/api/users/{author_id}/follow", response_model=SuccessSchema, status_code=status.HTTP_200_OK, tags=["users"]
)
async def unfollow_author(
    request: Request,
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
    make_context(request)
    api_key = await permission.get_api_key()
    result = await author.remove_follow(writing_author_id=author_id, api_key=api_key)
    logger.info("эндпоинт завершен", result=result.dict())
    return result
