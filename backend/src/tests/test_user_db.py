import pytest
from faker import Faker
from faker.providers import python
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app import app
from app_users.models import Author
from app_users.schemas import ProfileAuthorSchema, FollowAuthorSchema

from schemas import SuccessSchema

client = TestClient(app)

fake = Faker()
fake.add_provider(python)


@pytest.mark.asyncio
async def test_create_user(get_users_parameters, author_db_service):
    for user in get_users_parameters:
        result = await author_db_service.create_author(name=user[0], api_key=user[1], password=user[2])
        logger.info(result)
        assert isinstance(result, Author)
        assert result.name == user[0]
        assert result.api_key == user[1]
        assert result.password == user[2]


@pytest.mark.asyncio
async def test_create_user_error(get_users_parameters, author_db_service):
    for user in get_users_parameters:
        with pytest.raises(IntegrityError):
            await author_db_service.create_author(name=user[0], api_key=user[1], password=user[2])


@pytest.mark.asyncio
async def test_get_user(get_users_parameters, author_db_service):
    for user in get_users_parameters:
        result = await author_db_service.get_author(api_key=user[1])
        logger.info(result)
        assert isinstance(result, ProfileAuthorSchema)
        assert result.name == user[0]
        assert result.api_key == user[1]
        assert result.password == user[2]


@pytest.mark.asyncio
async def test_update_follow(get_users_parameters, author_db_service):
    users = []
    for user in get_users_parameters:
        users.append(await author_db_service.get_author(api_key=user[1]))

    logger.info(users)
    follower_0 = FollowAuthorSchema(id=users[0].id, name=users[0].name)
    follower_1 = FollowAuthorSchema(id=users[1].id, name=users[1].name)
    follower_2 = FollowAuthorSchema(id=users[2].id, name=users[2].name)

    assert follower_1 not in users[0].followers
    assert follower_2 not in users[0].followers
    assert follower_0 not in users[1].following
    assert follower_2 not in users[1].following

    result = await author_db_service.update_follow(reading_author=users[0],
                                         writing_author=users[1],
                                         followers=[follower_1.dict(), follower_2.dict()],
                                         following=[follower_0.dict(), follower_2.dict()],
                                         )
    assert isinstance(result, SuccessSchema)

    users = []
    for user in get_users_parameters:
        users.append(await author_db_service.get_author(api_key=user[1]))
    assert follower_1 in users[0].followers
    assert follower_2 in users[0].followers
    assert follower_0 in users[1].following
    assert follower_2 in users[1].following
    logger.info(users)

@pytest.mark.asyncio
async def test_update_follow(author_db_service):
    key = await author_db_service.verify_api_key_exist('11111')
    logger.info(f"test key: {key}")