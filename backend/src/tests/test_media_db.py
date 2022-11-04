"""
test_media_db.py
----------------

Модуль содержит тесты сервиса взаимодействия с СУБД приложения app_media
"""
import pytest
from faker import Faker
from faker.providers import python
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app import app
from app_media.db_services import MediaDbService
from app_media.schemas import MediaOrmSchema
from exceptions import BackendException

client = TestClient(app)

fake = Faker()
fake.add_provider(python)


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_create_media(session, get_media_parameters):
    """
    Тест сохранения картинки в СУБД.

    Parameters
    ----------
    session: pytest.fixture
        Фикстура возвращает асинхронную сессию SqlAlchemy.
    get_media_parameters: pytest.fixture
        Фикстура возвращает данные для заполнения СУБД.
    """
    await session
    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        result = await service.create_media(hash=param[0], file_name=param[1])
        logger.info(result)
        assert isinstance(result, MediaOrmSchema)
        assert result.hash == param[0]
        assert param[1] in result.link


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_create_media_error(get_media_parameters):
    """
    Тест исключения сохранения картинки в недоступную СУБД.

    Parameters
    ----------
    get_media_parameters: pytest.fixture
        Фикстура возвращает данные для заполнения СУБД.
    """

    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        with pytest.raises((IntegrityError, BackendException)):
            await service.create_media(hash=param[0], file_name=param[1])


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_get_media(get_media_parameters):
    """
    Тест получения картинки по хэшу

    Parameters
    ----------
    get_media_parameters: pytest.fixture
        Фикстура возвращает данные для заполнения СУБД.
    """
    service = MediaDbService()
    parameters = get_media_parameters
    for param in parameters:
        result = await service.get_media(hash=param[0])
        logger.info(result)
        assert isinstance(result, MediaOrmSchema)


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_get_many_media(get_media_parameters):
    """
    Тест получения нескольких картинок по списку идентификаторов.

    Parameters
    ----------
    get_media_parameters: pytest.fixture
        Фикстура возвращает данные для заполнения СУБД.
    """

    service = MediaDbService()
    parameters = get_media_parameters
    ids = []
    for param in parameters:
        result = await service.get_media(hash=param[0])
        ids.append(result.id)
    result = await service.get_many_media(ids)
    logger.info(ids)
    logger.info(result)
    assert len(result) == len(ids)
