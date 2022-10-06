import pytest
from loguru import logger
from sqlalchemy.exc import ProgrammingError

from app_users.schemas import ProfileAuthorOutSchema
from exceptions import BackendException
from schemas import SuccessSchema


@pytest.mark.asyncio
async def test_get_or_create_user(author_service):
    """тестирование недокументированного апи = получить или создать юзера"""
    api_key, created = await author_service.get_or_create_user('Авгерий', 'password')
    logger.info(api_key)
    logger.info(created)
    assert isinstance(api_key, str)
    assert isinstance(created, bool)
    assert created is True
    api_key, created = await author_service.get_or_create_user('Авгерий', 'password')
    logger.info(api_key)
    logger.info(created)
    assert isinstance(api_key, str)
    assert isinstance(created, bool)
    assert created is False


@pytest.mark.asyncio
async def test_generate_api_key(author_service):
    """тест генератора ключей"""
    key = author_service.generate_api_key(10)
    logger.info(key)
    assert isinstance(key, str)
    assert len(key) == 10


@pytest.mark.asyncio
async def test_me_service(get_users_parameters, get_authors, author_service):
    for user in get_users_parameters:
        result = await author_service.me(api_key=user[1])
        logger.info(result)
        assert isinstance(result, ProfileAuthorOutSchema)
        with pytest.raises(BackendException):
            await author_service.me(api_key=author_service.generate_api_key(10))


@pytest.mark.asyncio
async def test_get_author(get_authors, author_service):
    authors = await get_authors
    for author in authors:
        result = await author_service.get_author(author_id=author.user.id)
        assert isinstance(result, ProfileAuthorOutSchema)
        with pytest.raises(BackendException) or pytest.raises(ProgrammingError):
            await author_service.get_author(author_id='id')

        result = await author_service.get_author(api_key=author.user.api_key)
        assert isinstance(result, ProfileAuthorOutSchema)
        with pytest.raises(BackendException) or pytest.raises(ProgrammingError):
            await author_service.get_author(api_key=1)


@pytest.mark.asyncio
async def test_add_follow(author_service, get_authors):
    #todo = прикрутить фейкер
    authors = await get_authors
    result = await author_service.add_follow(
        writing_author_id=authors[0].user.id, api_key=authors[1].user.api_key)
    logger.info(result)
    assert isinstance(result, SuccessSchema)
