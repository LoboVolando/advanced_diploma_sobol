"""
urls.py
-------

Реализует эндпоинты для работы с твитами населения.
"""
from fastapi import APIRouter, Depends

from app_tweets.schemas import (
    TweetInSchema,
    TweetListOutSchema,
    TweetOutSchema,
    TweetSchema,
)
from app_tweets.services import TweetService
from app_users.services import PermissionService
from schemas import ErrorSchema, SuccessSchema

router = APIRouter()


@router.get("/api/tweets", response_model=TweetListOutSchema)
async def get_tweets_list(
    permission: PermissionService = Depends(), tweet: TweetService = Depends()
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
    api_key = await permission.get_api_key()
    return await tweet.get_list(api_key)


@router.post("/api/tweets")
async def create_tweet(
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
    api_key = await permission.get_api_key()
    return await tweet.create_tweet(new_tweet, api_key)


@router.get("/api/tweets/{tweet_id}")
async def get_tweet(
    tweet_id: int,
    tweet: TweetService = Depends(),
) -> TweetSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.
    """
    return await tweet.get_tweet(tweet_id=tweet_id)


@router.delete("/api/tweets/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.
    """
    api_key = await permission.get_api_key()
    return await tweet.delete_tweet(tweet_id=tweet_id, api_key=api_key)


@router.post("/api/tweets/{tweet_id}/likes")
async def add_like_to_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.
    """
    api_key = await permission.get_api_key()
    return await tweet.add_like_to_tweet(tweet_id=tweet_id, api_key=api_key)


@router.delete("/api/tweets/{tweet_id}/likes")
async def remove_like_from_tweet(
    tweet_id: int,
    permission: PermissionService = Depends(),
    tweet: TweetService = Depends(),
) -> SuccessSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема ошибки выполнения.
    """
    api_key = await permission.get_api_key()
    return await tweet.remove_like_from_tweet(tweet_id=tweet_id, api_key=api_key)
