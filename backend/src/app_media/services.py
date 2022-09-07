"""
services.py
-----------
Модуль реализует бизнес-логику приложения app_media
"""
import hashlib
import shutil
import typing as t
from pathlib import Path

from fastapi import UploadFile
from loguru import logger

from app_media.db_services import MediaDbService as MediaTransportService
from app_media.schemas import MediaOutSchema
from exceptions import BackendException, ErrorsList
from settings import settings


class MediaService:
    @staticmethod
    async def get_or_create_media(file: UploadFile) -> MediaOutSchema:
        """
        Метод сохраняет файл на сервере.

        Parameters
        ----------
        file: UploadFile
            Загруженный файл.

        Returns
        -------
        MediaOutSchema
            Pydantic-схема медиа-объекта для фронтенда.
        """
        bytez = await file.read()
        hash = hashlib.sha256(bytez).hexdigest()
        logger.warning(hash)
        if media := await MediaTransportService.get_media(hash=hash):
            return MediaOutSchema(media_id=media.id)
        MediaService.write_media_to_static_folder(file)
        if media := await MediaTransportService.create_media(hash=hash, file_name=file.filename):
            return MediaOutSchema(media_id=media.id)
        raise BackendException(**ErrorsList.media_import_error)

    @staticmethod
    def write_media_to_static_folder(file: UploadFile) -> None:
        """
        Метод записывает файл в папку на сервере.

        Parameters
        ----------
        file: UploadFile
            Загруженный файл.
        """
        path = Path(settings.media_root) / file.filename
        with open(path, "wb") as fl:
            file.file.seek(0)
            logger.info(f"запишем картинку в файл: {str(path)}")
            shutil.copyfileobj(file.file, fl)
            file.file.close()
        for file in Path(settings.media_root).glob("*.*"):
            logger.info(f"{file.absolute()}")

    @staticmethod
    async def get_many_media(ids: t.List[int]) -> t.Optional[t.List[str]]:
        """
        Метод запрашивает множество медиа-ресурсов по списку идентификаторов.

        Parameters
        ----------
        ids: List[int]
            Список идентификаторов.

        Returns
        -------
        List[str], optional
            Список URL ссылок на ресурсы, если они есть.
        List[]
            Пустой список, если ничего нет.
        """
        logger.info(f"запросим медиа по идентификаторам: {ids}")
        if attachments := await MediaTransportService.get_many_media(ids):
            return attachments
        return list()

    @staticmethod
    async def raise_exception():
        raise BackendException("test_exc", "мелкий зехер")
