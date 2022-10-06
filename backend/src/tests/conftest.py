import asyncio

import pytest
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db import Base
from settings import settings
from app_users.services import AuthorService
from app_users.db_services import AuthorDbService

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    logger.warning('run get eventloop')
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
    return AuthorService()

@pytest.fixture
def author_db_service():
    return AuthorDbService()
