import pytest
from loguru import logger
from sqlalchemy.exc import ProgrammingError

from app_users.schemas import *
from exceptions import BackendException
from schemas import SuccessSchema


@pytest.mark.service
@pytest.mark.asyncio
async def test_get_or_create_user(author_service, faker):
    """тестирование недокументированного апи = получить или создать юзера"""
    name = faker.name()
    password = faker.password()
    api_key, created = await author_service.get_or_create_user(name, password)
    logger.info(api_key)
    logger.info(created)
    assert isinstance(api_key, str)
    assert isinstance(created, bool)
    assert created is True
    api_key, created = await author_service.get_or_create_user(name, password)
    logger.info(api_key)
    logger.info(created)
    assert isinstance(api_key, str)
    assert isinstance(created, bool)
    assert created is False


@pytest.mark.service
@pytest.mark.asyncio
async def test_generate_api_key(author_service):
    """тест генератора ключей"""
    key = author_service.generate_api_key(10)
    logger.info(key)
    assert isinstance(key, str)
    assert len(key) == 10


@pytest.mark.service
@pytest.mark.asyncio
async def test_me_service(get_authors_api_key_list, author_service):
    api_list = await get_authors_api_key_list
    for api_key in api_list:
        result = await author_service.me(api_key=api_key)
        logger.info(result)
        assert isinstance(result, AuthorProfileApiSchema)
        assert set(result.dict().keys()) == {"result", "user"}
        assert result.result is True
        assert set(result.user.dict().keys()) == {"id", "name", "followers", "following"}
        with pytest.raises(BackendException):
            await author_service.me(api_key=author_service.generate_api_key(10))


@pytest.mark.service
@pytest.mark.asyncio
async def test_get_author_by_id(get_authors_id_list, author_service):
    ids = await get_authors_id_list
    for author_id in ids:
        result = await author_service.get_author(author_id=author_id)
        assert isinstance(result, AuthorProfileApiSchema)
        with pytest.raises(BackendException) or pytest.raises(ProgrammingError):
            await author_service.get_author(author_id="id")


@pytest.mark.service
@pytest.mark.asyncio
async def test_get_author_by_keys(get_authors_api_key_list, author_service):
    keys = await get_authors_api_key_list
    for key in keys:
        result = await author_service.get_author(api_key=key)
        assert isinstance(result, AuthorProfileApiSchema)
        with pytest.raises(BackendException) or pytest.raises(ProgrammingError):
            await author_service.get_author(api_key=1)


@pytest.mark.service
@pytest.mark.asyncio
async def test_add_remove_followers(get_authors_schemas_list, author_service, faker):
    """тестируем добавление фоловеров"""
    users = await get_authors_schemas_list
    reading_author = users[0]
    writing_author = users[1]
    result = await author_service.add_follow(writing_author.id, reading_author.api_key)
    reading_author = await author_service.get_author(author_id=reading_author.id)
    writing_author = await author_service.get_author(author_id=writing_author.id)
    new_follower = AuthorBaseSchema(id=writing_author.user.id, name=writing_author.user.name)
    new_following = AuthorBaseSchema(id=reading_author.user.id, name=reading_author.user.name)
    assert isinstance(result, SuccessSchema)
    assert new_follower.dict() in reading_author.user.followers
    assert new_following.dict() in writing_author.user.following
    reading_author = users[0]
    writing_author = users[1]
    result = await author_service.remove_follow(writing_author.id, reading_author.api_key)
    reading_author = await author_service.get_author(author_id=reading_author.id)
    writing_author = await author_service.get_author(author_id=writing_author.id)
    assert isinstance(result, SuccessSchema)
    assert new_follower.dict() not in reading_author.user.followers
    assert new_following.dict() not in writing_author.user.following
