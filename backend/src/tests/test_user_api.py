import pytest
from fastapi import status
from httpx import AsyncClient
from loguru import logger

from app_users.schemas import *
from schemas import SuccessSchema


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_create_api(faker, get_app):
    app = await get_app
    logger.info(type(app))
    data = dict(name=faker.name(), password=faker.password())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/register", headers={"api-key": "test"}, json=data)
        logger.info(response.json())
        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.json().keys()) == {"result", "api-key", "created"}


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_me_api(get_authors_api_key_list, faker, get_app):
    app = await get_app
    api_keys = await get_authors_api_key_list
    for key in api_keys:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/userinfo", headers={"api-key": key})
            assert response.status_code == status.HTTP_200_OK
            response_dict = response.json()
            response_schema = AuthorProfileApiSchema(**response_dict)
            assert isinstance(response_schema, AuthorProfileApiSchema)
            assert response_schema.result is True
            assert set(response_dict.keys()) == {"result", "user"}
            assert set(response_dict["user"].keys()) == {"id", "name", "followers", "following"}
    logger.info("test user me complete")


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_author_by_id_api(get_authors_id_list, get_app):
    app = await get_app
    ids = await get_authors_id_list
    logger.info(f"ids: {ids}")
    for author_id in ids:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/users/{author_id}", headers={"api-key": "test"})
            assert response.status_code == status.HTTP_200_OK
            response_dict = response.json()
            response_schema = AuthorProfileApiSchema(**response.json())
            assert isinstance(response_schema, AuthorProfileApiSchema)
            assert set(response_dict.keys()) == {"result", "user"}
            assert set(response_dict["user"].keys()) == {"id", "name", "followers", "following"}


@pytest.mark.api
@pytest.mark.asyncio
async def test_add_follow_api(get_authors_schemas_list, author_service, get_app):
    app = await get_app
    authors = await get_authors_schemas_list
    alpha_author = authors[0]
    for author in authors[1:]:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/api/users/{author.id}/follow", headers={"api-key": alpha_author.api_key})
            assert response.status_code == status.HTTP_200_OK
            response_dict = response.json()
            assert SuccessSchema() == SuccessSchema(**response_dict)
            response = await ac.delete(f"/api/users/{author.id}/follow", headers={"api-key": alpha_author.api_key})
            response_dict = response.json()
            assert SuccessSchema() == SuccessSchema(**response_dict)
            logger.info(response_dict)
