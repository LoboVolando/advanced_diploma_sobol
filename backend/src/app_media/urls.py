"""
urls.py
-------
Модуль определяет эндпоинты для работы с изображениями.
"""
import structlog
from fastapi import APIRouter, Request, UploadFile, status

from app_media.schemas import MediaOutSchema
from app_media.services import MediaService
from exceptions import BackendException, ErrorsList
from log_fab import make_context

router = APIRouter()

logger = structlog.get_logger()


@router.post("/api/medias", response_model=MediaOutSchema, status_code=status.HTTP_201_CREATED, tags=["media"])
async def medias(request: Request, file: UploadFile) -> MediaOutSchema:
    """
    Эндпоинт загружает файл с картинкой на сервер.

    Parameters
    ----------

    file: UploadFile
        Загружаемый файл.

    Returns
    -------
    MediaOutSchema
        Pydantic-схема медиа ресурса.
    """
    make_context(request)
    if result := await MediaService.get_or_create_media(file):
        logger.info(event="создан или получен media-объект", result=result.dict())
        return result
    logger.error(event="ошибка создания media-объекта")
    raise BackendException(**ErrorsList.media_import_error)


@router.get("/api/exception", tags=["media"])
async def raise_exception(request: Request):
    """Недокументированный эндпоинт. Выдаёт исключение при обращении."""
    make_context(request)
    logger.error(event="вызов ошибки")
    await MediaService.raise_exception()
