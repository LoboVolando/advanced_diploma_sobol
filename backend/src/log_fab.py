import logging
import sys
import uuid

import orjson
import structlog
from fastapi import Request


def get_logger():
    return structlog.get_logger()


class UrlVariables:
    @classmethod
    def make_context(cls, request: Request):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=str(uuid.uuid4()),
            view=request.url.path,
            method=request.method,
        )
