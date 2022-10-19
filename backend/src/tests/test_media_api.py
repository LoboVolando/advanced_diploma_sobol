import io

import pytest
from httpx import AsyncClient
from loguru import logger

from exceptions import BackendException


@pytest.mark.api
@pytest.mark.asyncio
async def test_media_exception(get_app):
    app = await get_app
    with pytest.raises(BackendException):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            await ac.get("/api/exception", headers={"api-key": "test"})


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_media(faker, get_app):
    app = await get_app
    image = io.BytesIO(faker.image(size=(100, 100), image_format="png"))
    files = {"file": (f"{faker.text(8)}png", image, "image/png")}
    with pytest.raises(BackendException):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/medias", headers={"api-key": "fake_api_key"}, files=files)
            logger.info(f"response: {response.json()}")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(url="/api/medias", headers={"api-key": "test"}, files=files)
    logger.info(response.json())
    response_dict = response.json()
    assert response.status_code == 201
    assert set(response_dict.keys()) == {"result", "media_id"}
    assert response_dict.get("result") is True
    assert isinstance(response_dict.get("media_id"), int)
    assert response_dict.get("media_id") > 0
