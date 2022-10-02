import pytest
import asyncio
from faker import Faker
from faker.providers import python
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import app
from app_media.db_services import MediaDbService
from app_media.schemas import MediaOrmSchema
from db import Base
from settings import settings

client = TestClient(app)

fake = Faker()
fake.add_provider(python)


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


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@pytest.mark.asyncio
async def test_create_media(session, get_media_parameters):
    await session
    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        result = await service.create_media(hash=param[0], file_name=param[1])
        logger.info(result)
        assert isinstance(result, MediaOrmSchema)
        assert result.hash == param[0]
        assert param[1] in result.link


@pytest.mark.asyncio
async def test_create_media_error(session, get_media_parameters):
    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        with pytest.raises(IntegrityError):
            await service.create_media(hash=param[0], file_name=param[1])


@pytest.mark.asyncio
async def test_get_media(get_media_parameters):
    """Тест получения картинки по хэшу"""
    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        result = await service.get_media(hash=param[0])
        logger.info(result)
        assert isinstance(result, MediaOrmSchema)


@pytest.mark.asyncio
async def test_get_many_media(get_media_parameters):
    service = MediaDbService()
    parameters = get_media_parameters
    ids = []
    for param in parameters:
        result = await service.get_media(hash=param[0])
        ids.append(result.id)
    result = await service.get_many_media(ids)
    logger.info(ids)
    logger.info(result)
