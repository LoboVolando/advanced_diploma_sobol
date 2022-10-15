import io

import pytest
from fastapi.testclient import TestClient
from loguru import logger

from app import app
from schemas import ErrorSchema
from exceptions import ErrorsList, BackendException

client = TestClient(app)


@pytest.mark.asyncio
async def test_media_exception():
    response = client.get('/api/exception', headers={"api-key": "test"})
    context = response.json()
    result = ErrorSchema(**context)
    logger.info(result)
    assert isinstance(result, ErrorSchema)
    assert response.status_code == 404
    assert set(list(context.keys())) == {"result", "error_type", "error_message"}


@pytest.mark.asyncio
async def test_create_media(faker):
    image = io.BytesIO(faker.image(size=(100, 100), image_format="png"))
    files = {"file": (f"{faker.text(8)}png", image, 'image/png')}
    response = client.post(url="/api/medias", headers={"api-key": "fake_api_key"}, files=files)
    assert response.status_code == 404
    assert BackendException(**response.json()) == BackendException(**ErrorsList.api_key_not_exists)
    response = client.post(url="/api/medias", headers={"api-key": "test"}, files=files)
    response_dict = response.json()
    assert response.status_code == 201
    assert set(response_dict.keys()) == {"result", "media_id"}
    assert response_dict.get("result") is True
    assert isinstance(response_dict.get("media_id"), int)
    assert response_dict.get("media_id") > 0
