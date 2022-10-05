from copy import copy
import io
from pathlib import Path
import random
import typing as t

import pytest
from PIL import Image
from fastapi import UploadFile
from loguru import logger

from app_media.schemas import MediaOutSchema
from app_media.services import MediaService


class RandomColorRectangle:
    def __init__(self):
        self.image = None
        self.stream = io.BytesIO()

    def random_rectangle(self, size_range: t.Tuple[int, int], color_range: tuple):
        self.image = Image.new("RGB",
                              (random.randint(size_range[0], size_range[1]),
                               random.randint(size_range[0], size_range[1])),
                              color=(random.randint(color_range[0], color_range[1]),
                                     random.randint(color_range[0], color_range[1]),
                                     random.randint(color_range[0], color_range[1]))
                              )
        self.image.save(self.stream, "png")
        self.stream.seek(0)
        return self

    def show(self):
        return self.image.show()

    def as_file_object(self):
        return self.stream

    def as_upload_file(self):
        return UploadFile(filename=f'{random.randint(100, 100000)}.png', file=self.stream, content_type='image/png')


@pytest.mark.asyncio
async def test_get_or_create_media():
    logger.warning('test get or create media')
    service = MediaService()
    file = RandomColorRectangle().random_rectangle((50, 70), (100, 250)).as_upload_file()
    result = await service.get_or_create_media(copy(file))
    assert isinstance(result, MediaOutSchema)
    assert hasattr(result, 'result')
    assert hasattr(result, 'media_id')
    assert result.result is True
    assert isinstance(result.media_id, int)
    logger.warning(result)


@pytest.mark.asyncio
async def test_get_or_create_media_error():
    logger.warning('test get or create media error')
    service = MediaService()
    file = RandomColorRectangle().random_rectangle((50, 70), (100, 250)).as_upload_file()
    result = await service.get_or_create_media(file)
    assert isinstance(result, MediaOutSchema)
    assert hasattr(result, 'result')
    assert hasattr(result, 'media_id')
    assert result.result is True
    assert isinstance(result.media_id, int)
    logger.warning(result)


@pytest.mark.asyncio
async def test_write_file_to_static():
    logger.warning('test write file to static')
    service = MediaService()
    file = RandomColorRectangle().random_rectangle((50, 70), (100, 250)).as_file_object()
    file_name = f'{random.randint(1000, 2000)}.png'
    upload_file = UploadFile(filename=file_name, file=file, content_type='image/png')
    path = service.write_media_to_static_folder(upload_file)
    assert isinstance(path, Path)
    assert path.exists()
    assert path.stat().st_size > 0
    logger.info(path)
