import pytest
from faker import Faker
from faker.providers import python
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import app
from app_media.db_services import MediaDbService
from app_media.schemas import MediaOrmSchema

client = TestClient(app)

fake = Faker()
fake.add_provider(python)


@pytest.fixture()
async def session():
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from settings import settings
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
    from db import Base
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
async def test_create_media(session):
    await session
    service = MediaDbService()
    result = await service.create_media(hash='111', file_name='test_file.jpg')
    logger.info(result)
    assert isinstance(result, MediaOrmSchema)
    assert result.hash == '111'
    assert 'test_file.jpg' in result.link
    with pytest.raises(IntegrityError):
        await service.create_media(hash='111', file_name='test_file.jpg')


@pytest.mark.asyncio
async def test_get_media():
    """Тест получения картинки по хэшу"""
    service = MediaDbService()
    result = await service.get_media(hash='111')
    logger.info(result)
    logger.info('testtesttest media')
