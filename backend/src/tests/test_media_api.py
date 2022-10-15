import io

import pytest
from loguru import logger
from httpx import AsyncClient

from schemas import ErrorSchema
from exceptions import ErrorsList, BackendException



# @pytest.mark.api
# @pytest.mark.asyncio
# async def test_media_exception(get_app):
#     app = await get_app
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get('/api/exception', headers={"api-key": "test"})
#     context = response.json()
#     result = ErrorSchema(**context)
#     logger.info(result)
#     assert isinstance(result, ErrorSchema)
#     assert response.status_code == 404
#     assert set(list(context.keys())) == {"result", "error_type", "error_message"}
#
#
@pytest.mark.api
@pytest.mark.asyncio
async def test_create_media(faker, get_app):
    app = await get_app
    image = io.BytesIO(faker.image(size=(100, 100), image_format="png"))
    files = {"file": (f"{faker.text(8)}png", image, 'image/png')}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        with pytest.raises(BackendException):
            response = await ac.post('/api/medias', headers={"api-key": "fake_api_key"}, files=files)
            logger.info(f"response: {response.json()}")
    # assert response.status_code == 404
    # assert BackendException(**response.json()) == BackendException(**ErrorsList.api_key_not_exists)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(url="/api/medias", headers={"api-key": "test"}, files=files)
    logger.info(response.json())
    response_dict = response.json()
    assert response.status_code == 201
    assert set(response_dict.keys()) == {"result", "media_id"}
    assert response_dict.get("result") is True
    assert isinstance(response_dict.get("media_id"), int)
    assert response_dict.get("media_id") > 0
#