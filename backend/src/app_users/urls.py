"""
urls.py
-------
Модуль реализует эндпоинты приложения app_users.
"""
from fastapi import APIRouter, Depends
from loguru import logger

from app_users.exceptions import PasswordIncorrectException
from app_users.schemas import ProfileAuthorOutSchema, RegisterAuthorSchema
from app_users.services import AuthorService, PermissionService
from schemas import ErrorSchema, SuccessSchema

router = APIRouter()


@router.post("/api/register")
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
    try:
        api_key, created = await service.get_or_create_user(name=author.name, password=author.password)
        logger.info(api_key)
        return {"result": "true", "api-key": api_key, "created": created}
    except PasswordIncorrectException:
        ErrorSchema(
            error_type="INCORRECT_PASSWROR",
            error_message=f"неверный пароль для: {author.name}",
        ).dict()


@router.get("/api/userinfo")
@router.get("/api/users/me")
async def me(
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> ProfileAuthorOutSchema | ErrorSchema:
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
    ErrorSchema
        pydantic-схема сообщения об ошибке.
    """
    api_key = await permission.get_api_key()
    return await user.me(api_key)


@router.get("/api/users/{author_id}")
async def get_author_by_id(
    author_id: int,
    user: AuthorService = Depends(),
    permission: PermissionService = Depends(),
) -> ProfileAuthorOutSchema | ErrorSchema:
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
    ErrorSchema
        pydantic-схема сообщения об ошибке.

    """
    await permission.get_api_key()
    logger.info("run api")
    return await user.get_author(author_id=author_id)


@router.post("/api/users/{author_id}/follow")
async def follow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
) -> SuccessSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.

    Note
    ----
    Идентификатор читающего автора извлекается при помощи зависимости permission.
    """
    api_key = await permission.get_api_key()
    return await author.add_follow(writing_author_id=author_id, api_key=api_key)


@router.delete("/api/users/{author_id}/follow")
async def unfollow_author(
    author_id: int,
    permission: PermissionService = Depends(),
    author: AuthorService = Depends(),
) -> SuccessSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.

    Note
    ----
    Идентификатор читающего автора извлекается при помощи зависимости permission.
    """

    api_key = await permission.get_api_key()
    return await author.remove_follow(writing_author_id=author_id, api_key=api_key)
