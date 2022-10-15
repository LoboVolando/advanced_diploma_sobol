import asyncio
import typing as t
from fastapi import FastAPI, Depends
import pytest
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db import Base
from settings import settings
from app import verify_api_key
from app_media import router as app_media_router
from app_tweets import router as app_tweets_router
from app_users import router as app_users_router

from app_users.services import AuthorService
from app_media.services import MediaService
from app_users.db_services import AuthorDbService
from app_tweets.db_services import TweetDbService
from app_tweets.services import TweetService
from faker import Factory
from tests.test_media_service import RandomColorRectangle

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    logger.warning('run get eventloop')
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def get_app():
    app = FastAPI(
        title="CLI-ter",
        description="Импортозамещение in action",
        version="0.01a",
        docs_url='/api/docs',
        openapi_url="/api/v1/openapi.json",
        dependencies=[Depends(verify_api_key)],
    )
    app.include_router(app_tweets_router)
    app.include_router(app_users_router)
    app.include_router(app_media_router)

    return app

@pytest.fixture(scope="session")
async def session():
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
        logger.info('recreated metadata')
    logger.info('fixture connection created')
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture()
async def simple_session():
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
    logger.info('simple fixture connection created')
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture
def get_media_parameters():
    return [("111", "file1.jpg"), ("222", "file2.jpg"), ("333", "file3.jpg")]

@pytest.fixture
def get_users_parameters():
    return [("Ivan", "key_1", "pass_1"), ("Stepan", "key_2", "pass_2"), ("Vovan", "key_3", "pass_3")]

@pytest.fixture
async def get_authors(get_users_parameters):
    service = AuthorService()
    users = []
    for user in get_users_parameters:
        users.append(await service.me(api_key=user[1]))
    logger.info(users)
    return users

@pytest.fixture
def author_service():
    service = AuthorService()
    assert isinstance(service.service, AuthorDbService)
    return service

@pytest.fixture
def media_service():
    service = MediaService()
    return service

@pytest.fixture
def author_db_service():
    return AuthorDbService()

@pytest.fixture
def tweet_db_service():
    return TweetDbService()

@pytest.fixture
def tweet_service():
    return TweetService()

@pytest.fixture
def media_service():
    return MediaService()

@pytest.fixture
def faker():
    fake = Factory.create('ru-RU')
    return fake

@pytest.fixture
async def create_authors(author_count: int, faker, author_db_service) -> t.List[int]:
    ids = []
    for _ in range(author_count):
        author = await author_db_service.create_author(
            name=faker.name(), password=faker.password(), api_key=faker.pystr(min_chars=64, max_chars=64))
        ids.append(author.id)
    return ids

