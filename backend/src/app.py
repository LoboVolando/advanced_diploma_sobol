"""
app.py
------

Главный модуль приложения. разделён на 3 приложения: app_users app_tweets app_media. Точка входа для wsgi http сервера.

Examples
--------
Пример запуска приложения через сервер **gunicorn**::

    $ gunicorn app:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind backend:80

Note
----
    Каждое приложение имеет единую структуру модулей:

    urls.py
        модуль эндпоинтов
    schemas.py
        модуль pydantic-схем для обмена и валидации данных
    models.py
        модуль с моделями ORM SqlAlchemy
    services.py
        модуль с бизнес-логикой
    interfaces.py
        модуль с абстрактными классами для реализации взаимодействия с СУБД
    db_services.py
        конкретная реализация работы с СУБД

Attributes
----------
app : FastAPI
    Экземпляр приложения FastApi, к которому подключаются middleware и роуты приложений
"""
from fastapi import Depends, FastAPI, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app_media import router as app_media_router
from app_tweets import router as app_tweets_router
from app_users import router as app_users_router
from app_users.services import PermissionService
from exceptions import (
    AuthException,
    BackendException,
    ErrorsList,
    InternalServerException,
)
from tags import tags_metadata


async def verify_api_key(api_key: str = Header(), permission: PermissionService = Depends()):
    """Зависимость проверяет api-key при каждом запросе"""
    logger.info(f"api_key: {api_key}")
    if not api_key:
        raise BackendException(**ErrorsList.not_authorized)
    if api_key == "test":
        return True
    if not await permission.verify_api_key(api_key):
        raise BackendException(**ErrorsList.api_key_not_exists)
    return True


app = FastAPI(
    title="CLI-ter",
    description="Импортозамещение in action",
    version="0.01a",
    openapi_tags=tags_metadata,
    docs_url="/api/docs",
    openapi_url="/api/v1/openapi.json",
    dependencies=[Depends(verify_api_key)],
)


@app.exception_handler(BackendException)
async def media_exception_handler(request: Request, exc: BackendException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"result": exc.result, "error_type": exc.error_type, "error_message": exc.error_message},
    )


@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"result": exc.result, "error_type": exc.error_type, "error_message": exc.error_message},
    )


@app.exception_handler(InternalServerException)
async def internal_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"result": exc.result, "error_type": exc.error_type, "error_message": exc.error_message},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_tweets_router)
app.include_router(app_users_router)
app.include_router(app_media_router)
