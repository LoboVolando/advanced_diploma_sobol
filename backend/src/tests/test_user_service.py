import typing

import pytest
from loguru import logger
from sqlalchemy.exc import ProgrammingError

from app_users.schemas import ProfileAuthorOutSchema
from exceptions import BackendException

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
async def test_me_service(get_users_parameters, author_service):
    for user in get_users_parameters:
        result = await author_service.me(api_key=user[1])
        logger.info(result)
        assert isinstance(result, ProfileAuthorOutSchema)
        with pytest.raises(BackendException):
            await author_service.me(api_key=author_service.generate_api_key(10))


@pytest.mark.service
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


@pytest.mark.service
@pytest.mark.asyncio
async def test_add_followers(author_service, faker):
    """тестируем добавление фоловеров"""
    users_count = 5
    api_keys, users = await register_fake_users(users_count, author_service, faker)

    read_user = users[0]
    followers = users[1:]
    await check_followers_for_user(author_service, read_user, followers)
    await check_following_for_user(author_service, followers, 1)


async def register_fake_users(count: int, author_service, faker) -> tuple[typing.List[str], typing.List[ProfileAuthorOutSchema]]:
    """регистрируем произвольное количество фейковых юзеров в базе"""
    api_keys = []
    users = []
    for _ in range(count):
        key = await author_service.get_or_create_user(name=faker.name(), password=faker.password())
        logger.info(key[0])
        api_keys.append(key[0])
        users.append(await author_service.get_author(api_key=key[0]))
    logger.info(api_keys)
    logger.info(users)
    assert len(api_keys) == count
    assert len(users) == count
    return api_keys, users


async def check_followers_for_user(author_service,
                                   read_user: ProfileAuthorOutSchema,
                                   followers: typing.List[ProfileAuthorOutSchema]):
    """тестируем количество добавленных юзеров в фоловеры"""
    folowers_count_before = len(read_user.user.followers)
    assert folowers_count_before == 0
    for user in followers:
        assert len(user.user.following) == 0
        await author_service.add_follow(user.user.id, read_user.user.api_key)
    read_user = await author_service.get_author(author_id=read_user.user.id)
    logger.info(f"followers: {read_user.user.followers}")
    assert len(read_user.user.followers) == len(followers)

async def check_following_for_user(author_service,
                                   followers: typing.List[ProfileAuthorOutSchema], following_count: int):
    """тестируем фолофингов"""
    for user in followers:
        user = await author_service.get_author(author_id=user.user.id)
        assert len(user.user.following) == following_count
