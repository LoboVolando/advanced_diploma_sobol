"""
urls.py
-------
Модуль определяет эндпоинты для работы с изображениями.
"""
from fastapi import APIRouter, UploadFile, status

from app_media.schemas import MediaOutSchema
from app_media.services import MediaService

router = APIRouter()


@router.post("/api/medias", response_model=MediaOutSchema, status_code=status.HTTP_201_CREATED)
async def medias(file: UploadFile) -> MediaOutSchema:
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
    if result := await MediaService.get_or_create_media(file):
        return result


@router.get("/api/exception")
async def raise_exception():
    """Недокументированный эндпоинт. Выдаёт исключение при обращении."""

    await MediaService.raise_exception()
