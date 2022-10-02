import asyncio

import pytest
from loguru import logger


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    logger.warning('run get eventloop')
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def get_media_parameters():
    return [("111", "file1.jpg"), ("222", "file2.jpg"), ("333", "file3.jpg")]
