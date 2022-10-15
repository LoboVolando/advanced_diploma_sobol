import io
import json
import pytest
from httpx import AsyncClient
from fastapi import status
from loguru import logger

# from app import app
from app_users.services import AuthorService
from schemas import ErrorSchema, SuccessSchema
from exceptions import ErrorsList, BackendException
from tests.test_user_service import register_fake_users


@pytest.mark.api
@pytest.mark.asyncio
async def test_user_create_api(faker, get_app):
    app = await get_app
    logger.info(type(app))
    data = dict(name=faker.name(), password=faker.password())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post('/api/register', headers={"api-key": "test"}, json=data)
    context = response.json()
    logger.info(f"context: {context}")
    # assert response.status_code == status.HTTP_201_CREATED
    # assert set(context.keys()) == {"result", "api-key", "created"}
    # assert context['result'] is True


# @pytest.mark.api
# @pytest.mark.asyncio
# async def test_user_me(faker, get_app):
#     app = await get_app
#     api_keys, users = await register_fake_users(count=4, faker=faker, author_service=AuthorService())
#     logger.warning(users)
#     for user in users:
#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.get('/api/userinfo', headers={"api-key": user.user.api_key})
#             logger.info(response.json())
