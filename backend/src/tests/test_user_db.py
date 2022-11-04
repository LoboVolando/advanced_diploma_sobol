import pytest
from faker import Faker
from faker.providers import python
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.exc import IntegrityError, ProgrammingError

from app import app
from app_users.schemas import *
from exceptions import BackendException
from schemas import SuccessSchema

client = TestClient(app)

fake = Faker()
fake.add_provider(python)


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_create_user(faker, author_db_service):
    fake_users = []
    user_count = 5
    for _ in range(user_count):
        name = faker.name()
        key = faker.pystr()
        password = faker.password()
        result = await author_db_service.create_author(name=name, api_key=key, password=password)
        fake_users.append(result)
        assert isinstance(result, AuthorModelSchema)
        assert result.name == name
        assert result.api_key == key
        assert result.password == password
    for user in fake_users:
        with pytest.raises(BackendException):
            await author_db_service.create_author(name=user.name, api_key=user.api_key, password=faker.password())


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_get_user(get_authors_schemas_list, author_db_service):
    users = await get_authors_schemas_list
    for user in users:
        result = await author_db_service.get_author(api_key=user.api_key)
        assert isinstance(result, AuthorModelSchema)
        assert result.name == user.name
        assert result.api_key == user.api_key
        assert result.password == user.password


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_update_follow(get_authors_schemas_list, author_db_service):
    users = await get_authors_schemas_list
    assert len(users) > 1
    followings = users[1:]
    for user in users:
        assert isinstance(user, AuthorModelSchema)

    for user in followings:
        result = await author_db_service.update_follow(
            reading_author=users[0],
            writing_author=user,
            followers=[u.dict(include={"id", "name"}) for u in followings],
            following=[users[0].dict(include={"id", "name"})],
        )
        assert isinstance(result, SuccessSchema)
        following = await author_db_service.get_author(api_key=user.api_key)
        follower = await author_db_service.get_author(api_key=users[0].api_key)
        assert users[0].dict(include={"id", "name"}) in following.following
        assert user.dict(include={"id", "name"}) in follower.followers
