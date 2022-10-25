"""
conftest.py
-----------

Модуль содержит фикстуры для фреймворка тестирования pytest
"""
import asyncio

import pytest
from faker import Factory
from fastapi import Depends, FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import verify_api_key
from app_media import router as app_media_router
from app_tweets import router as app_tweets_router
from app_tweets.db_services import TweetDbService
from app_tweets.schemas import *
from app_tweets.services import TweetService
from app_users import router as app_users_router
from app_users.db_services import AuthorDbService
from app_users.schemas import *
from app_users.services import AuthorService
from db import Base
from settings import settings

user_count = 6


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """
    Фикстура получает запущенный цикл событий.

    Yields
    ------
    loop
    """
    logger.warning("run get eventloop")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def get_app():
    """
    Фикстура возвращает экземпляр приложения FastAPI.

    Returns
    -------
    FastAPI
        Экземпляр приложения.
    """
    app = FastAPI(
        title="CLI-ter",
        description="Импортозамещение in action",
        version="0.01a",
        docs_url="/api/docs",
        openapi_url="/api/v1/openapi.json",
        dependencies=[Depends(verify_api_key)],
    )
    app.include_router(app_tweets_router)
    app.include_router(app_users_router)
    app.include_router(app_media_router)

    return app


@pytest.fixture(scope="session")
async def session():
    """
    Фикстура возвращает асинхронную снссию SqlAlchemy.
    База данных при этом уничтожается и создаётся вновь.

    Returns
    -------
    AsyncSession
        Экземпляр сессии.
    """
    credentials = dict(
        user=settings.postgres_root_user,
        password=settings.postgres_root_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        db=settings.web_db,
    )
    engine = create_async_engine(
        "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(**credentials),
        echo=False,
    )
    logger.info(Base.metadata.tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("recreated metadata")
    logger.info("fixture connection created")
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture()
async def simple_session():
    """
    Фикстура возвращает асинхронную снссию SqlAlchemy.

    Returns
    -------
    AsyncSession
        Экземпляр сессии.
    """
    credentials = dict(
        user=settings.postgres_root_user,
        password=settings.postgres_root_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        db=settings.web_db,
    )
    engine = create_async_engine(
        "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(**credentials),
        echo=False,
    )
    logger.info("simple fixture connection created")
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def get_media_parameters():
    """
    Фикстура возвращает список кортежей непонятно зачем. Но если работает - не трогай.

    Returns
    -------
    List
        Список кортежей.
    """
    return [("111", "file1.jpg"), ("222", "file2.jpg"), ("333", "file3.jpg")]


@pytest.fixture
def author_service():
    """
    Фикстура возвращает экземпляр сервиса. Слой бизнес-логики.

    Returns
    -------
    AuthorService
        Сервис бизнес-логики.
    """
    service = AuthorService()
    assert isinstance(service.service, AuthorDbService)
    return service


@pytest.fixture
def tweet_service():
    """
    Фикстура возвращает экземпляр сервиса. Слой бизнес-логики.

    Returns
    -------
    TweetService
        Сервис бизнес-логики.
    """
    return TweetService()


@pytest.fixture
def author_db_service():
    """
    Фикстура возвращает экземпляр сервиса. Слой работы с БД.

    Returns
    -------
    AuthorDbService
        Сервис работы с БД.
    """
    return AuthorDbService()


@pytest.fixture
def tweet_db_service():
    """
    Фикстура возвращает экземпляр сервиса. Слой работы с БД.

    Returns
    -------
    TweetDbService
        Сервис работы с БД.
    """
    return TweetDbService()


@pytest.fixture
def faker():
    """
    Фикстура возвращает фейкер.

    Returns
    -------
    Factory
        Генератор фейков.
    """
    fake = Factory.create("ru-RU")
    return fake


@pytest.fixture
async def get_authors_id_list(faker, author_db_service) -> t.List[int]:
    """
    Фикстура добавляет в субд некоторое количество авторов.

    Parameters
    ----------
    faker:
        Фикстура фейковых данных.
    author_db_service:
        Фикстура сервиса СУБД авторов.

    Returns
    -------
    List[int]
        Список идентификаторов авторов.
    """
    ids = []
    for _ in range(user_count):
        author = await author_db_service.create_author(
            name=faker.name(), password=faker.password(), api_key=faker.pystr(min_chars=64, max_chars=64)
        )
        ids.append(author.id)
    return ids


@pytest.fixture
async def get_authors_api_key_list(faker, author_db_service) -> t.List[str]:
    """
    Фикстура добавляет в субд некоторое количество авторов.

    Parameters
    ----------
    faker:
        Фикстура фейковых данных.
    author_db_service:
        Фикстура сервиса СУБД авторов.

    Returns
    -------
    List[str]
        Список api-ключей.
    """
    api_keys = []
    for _ in range(user_count):
        author = await author_db_service.create_author(
            name=faker.name(), password=faker.password(), api_key=faker.pystr(min_chars=64, max_chars=64)
        )
        api_keys.append(author.api_key)
    return api_keys


@pytest.fixture
async def get_authors_schemas_list(faker, author_db_service) -> t.List[AuthorModelSchema]:
    """
    Фикстура добавляет в субд некоторое количество авторов.

    Parameters
    ----------
    faker:
        Фикстура фейковых данных.
    author_db_service:
        Фикстура сервиса СУБД авторов.

    Returns
    -------
    List[AuthorModelSchema]
        Список Pydantic-схем orm моделей.
    """
    authors_list = []
    for _ in range(user_count):
        author = await author_db_service.create_author(
            name=faker.name(), password=faker.password(), api_key=faker.pystr(min_chars=64, max_chars=64)
        )
        authors_list.append(author)
    return authors_list


@pytest.fixture
async def get_tweet_schemas_list(
        faker, get_authors_schemas_list, tweet_db_service
) -> t.Tuple[t.List[AuthorModelSchema], t.List[TweetModelSchema]]:
    """
    Фикстура добавляет в субд некоторое количество авторов и твитов.

    Parameters
    ----------
    faker:
        Фикстура фейковых данных.
    get_authors_schemas_list:
        Фикстура добавления авторов в СУБД.
    tweet_db_service:
        Фикстура сервису СУБД твитов.

    Returns
    -------
    Tuple[List[AuthorModelSchema], List[TweetModelSchema]]
        Кортеж списков Pydantic-схем orm моделей авторов и их твитов.
    """

    authors_list = await get_authors_schemas_list
    tweet_list = []
    tweet_count = 10
    for author in authors_list:
        for _ in range(tweet_count):
            new_tweet = TweetInSchema(tweet_data=faker.text(200))
            tweet_list.append(await tweet_db_service.create_tweet(new_tweet, author.id, []))
    return authors_list, tweet_list
