"""
urls.py
-------

Реализует эндпоинты для работы с твитами населения.
"""
from fastapi import APIRouter, Depends, Request, status

from app_tweets.schemas import (
    TweetInSchema,
    TweetListOutSchema,
    TweetModelOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_tweets.services import TweetService
from app_users.services import PermissionService
from log_fab import UrlVariables, get_logger
from schemas import SuccessSchema

router = APIRouter()
logger = get_logger()


@router.get("/api/tweets", response_model=TweetListOutSchema, status_code=status.HTTP_200_OK, tags=["tweets"])
async def get_tweets_list(
    request: Request, permission: PermissionService = Depends(), tweet: TweetService = Depends()
) -> TweetListOutSchema:
    """Эндпоинт реализует получение всех твитов текущего автора.

    Parameters
    ----------
    permission: PermissionService
        Зависимость для работы с правами.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов.

    Returns
    -------
    TweetListOutSchema
        Pydantic-схема списка твитов.
    """
    logger.debug("begin endpoint")
    api_key = await permission.get_api_key()
    result = await tweet.get_list(api_key)
    logger.info(f"вызов эндпоинта завершен успешно")
    return result


@router.post("/api/tweets", response_model=TweetOutSchema, status_code=status.HTTP_201_CREATED, tags=["tweets"])
async def create_tweet(
    request: Request,
    new_tweet: TweetInSchema,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> TweetOutSchema:
    """Эндпоинт сохранения нового твита в системе.

    Parameters
    ----------
    new_tweet: TweetInSchema
        Pydantic-схема нового твита от фронтенда.
    permission: PermissionService
        Зависимость для работы с правами.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов.

    Returns
    -------
    TweetOutSchema
        Pydantic-схема для фронтенда вновь созданного твита
    """
    UrlVariables.make_context(request)
    api_key = await permission.get_api_key()
    result = await tweet.create_tweet(new_tweet, api_key)
    logger.info(event="вызов эндпоинта завершен успешно")
    return result


@router.get(
    "/api/tweets/{tweet_id}", response_model=TweetModelOutSchema, status_code=status.HTTP_200_OK, tags=["tweets"]
)
async def get_tweet(
    request: Request,
    tweet_id: int,
    tweet: TweetService = Depends(),
) -> TweetModelOutSchema:
    """Эндпоинт достаёт твит по идентификатору СУБД.

    Parameters
    ----------
    tweet_id: int
        Идентификатор твита в СУБД.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов.

    Returns
    -------
    TweetSchema
        Pydantic-схема для фронтенда твита.
    """
    UrlVariables.make_context(request)
    result = await tweet.get_tweet(tweet_id=tweet_id)
    logger.info(event="вызов эндпоинта завершен успешно")
    return result


@router.delete("/api/tweets/{tweet_id}", response_model=SuccessSchema, status_code=status.HTTP_200_OK, tags=["tweets"])
async def delete_tweet(
    request: Request,
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema:
    """Эндпоинт удаления твита.

    Parameters
    ----------
    tweet_id: int
        Идентификатор твита в СУБД.
    permission: PermissionService
        Зависимость для работы с правами.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов

    Returns
    -------
    SuccessSchema
        Pydantic-схема успешного выполнения.
    """
    UrlVariables.make_context(request)
    api_key = await permission.get_api_key()
    result = await tweet.delete_tweet(tweet_id=tweet_id, api_key=api_key)
    logger.info(event="вызов эндпоинта завершен успешно")
    return result


@router.post(
    "/api/tweets/{tweet_id}/likes", response_model=SuccessSchema, status_code=status.HTTP_200_OK, tags=["tweets"]
)
async def add_like_to_tweet(
    request: Request,
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema:
    """Эндпоинт добавляет лайку к твиту.

    Parameters
    ----------
    tweet_id: int
        Идентификатор твита в СУБД.
    permission: PermissionService
        Зависимость для работы с правами.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов

    Returns
    -------
    SuccessSchema
        Pydantic-схема успешного выполнения.
    """
    UrlVariables.make_context(request)
    api_key = await permission.get_api_key()
    result = await tweet.add_like_to_tweet(tweet_id=tweet_id, api_key=api_key)
    logger.info(event="вызов эндпоинта завершен успешно")
    return result


@router.delete(
    "/api/tweets/{tweet_id}/likes", response_model=SuccessSchema, status_code=status.HTTP_200_OK, tags=["tweets"]
)
async def remove_like_from_tweet(
    request: Request,
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema:
    """Эндпоинт удаляет лайку с твита.

    Parameters
    ----------
    tweet_id: int
        Идентификатор твита в СУБД.
    permission: PermissionService
        Зависимость для работы с правами.
    tweet: TweetService
        Зависимость для работы с бизнес-логикой твитов

    Returns
    -------
    SuccessSchema
        Pydantic-схема успешного выполнения.
    """
    UrlVariables.make_context(request)
    api_key = await permission.get_api_key()
    result = await tweet.remove_like_from_tweet(tweet_id=tweet_id, api_key=api_key)
    logger.info(event="вызов эндпоинта завершен успешно")
    return result
