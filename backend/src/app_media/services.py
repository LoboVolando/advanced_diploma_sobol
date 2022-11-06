"""
services.py
-----------
Модуль реализует бизнес-логику приложения app_media

"""
import hashlib
import shutil
import typing as t
from pathlib import Path

import structlog
from fastapi import UploadFile
from pydantic import ValidationError

from app_media.db_services import MediaDbService as MediaTransportService
from app_media.schemas import MediaOutSchema
from exceptions import BackendException, ErrorsList
from settings import settings

logger = structlog.get_logger()


class MediaService:
    """Класс реализует бизнес-логику работы с медиа-файлами."""

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
        logger.info(event="расчитан хэш для файла", hash=hash, file=file.filename, content_type=file.content_type)
        if media := await MediaTransportService().get_media(hash=hash):
            result = MediaOutSchema(media_id=media.id)
            logger.info("файл уже существует", result=result.dict())
            return result
        MediaService.write_media_to_static_folder(file)
        if media := await MediaTransportService().create_media(hash=hash, file_name=file.filename):
            try:
                result = MediaOutSchema(media_id=media.id)
            except ValidationError as e:
                logger.exception(event="ошибка сериализации", exc_info=e)
                raise BackendException(**ErrorsList.serialize_error)
            else:
                logger.info("возвращаем объект", result=result.dict())
                return result
        logger.error(event="ошибка получения или сохранения медиа-объекта")
        raise BackendException(**ErrorsList.media_import_error)

    @staticmethod
    def write_media_to_static_folder(file: UploadFile) -> Path:
        """
        Метод записывает файл в папку на сервере.

        Parameters
        ----------
        file: UploadFile
            Загруженный файл.

        Returns
        -------
        Path
            путь к файлу
        """
        path = Path(settings.docker_media_root) / file.filename
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True)
            except PermissionError as e:
                logger.error(f"нет прав на создание директории: {path.parent}")
                logger.exception(e)
            else:
                logger.warning(event="создали директорию для файла", folder=path.parent.absolute())
        with open(path, "wb") as fl:
            try:
                file.file.seek(0)
                logger.info(event="запись файла", path=path)
                shutil.copyfileobj(file.file, fl)
                file.file.close()
            except Exception as e:
                logger.exception(event="непредвиденная ошибка сохранения файла", exc_info=e)
                raise BackendException(**ErrorsList.media_import_error)
            else:
                logger.info(event="возврат файлового пути", path=path)
                return path

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
        if attachments := await MediaTransportService().get_many_media(ids):
            logger.info(event="запросим медиа по списку идентификаторов", id_list=ids, attachments=attachments)
            return attachments
        logger.warning(event="очень странно, но по списку id не нашлось ничего", id_list=ids)
        return list()

    @staticmethod
    async def raise_exception():
        logger.info(event="поднимаем тестовое исключение")
        raise BackendException("test_exc", "мелкий зехер")
