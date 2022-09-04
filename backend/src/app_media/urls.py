"""
urls.py
-------
Модуль определяет эндпоинты для работы с изображениями.
"""
from fastapi import APIRouter, UploadFile

from app_media.services import MediaService
from app_media.schemas import MediaOutSchema
from schemas import ErrorSchema

router = APIRouter()


@router.post("/api/medias")
async def medias(file: UploadFile) -> MediaOutSchema | ErrorSchema:
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
    ErrorSchema
        Pydantic-схема сообщения об ошибке.
    """
    if result := await MediaService.get_or_create_media(file):
        return result
