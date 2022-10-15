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



@pytest.mark.anyio
async def test_user_create_api(faker):
    data = dict(name=faker.name(), password=faker.password())
    logger.info(data)
    response = client.post('/api/register', headers={"api-key": "test"}, data=json.dumps(data, ensure_ascii=False))
    context = response.json()
    logger.info(response.status_code)
    logger.warning(response.json())
    assert response.status_code == status.HTTP_201_CREATED
    assert set(context.keys()) == {"result", "api-key", "created"}
    assert context['result'] is True

@pytest.mark.anyio
async def test_user_me(create_authors, event_loop):
    users = await register_fake_users(count=4, faker=faker, author_service=AuthorService(), loope=event_loop)
    logger.warning(users)
