"""
db_services.py
--------------
Модуль реализует классы для взаимодействия между бизнес-логикой и СУБД.
"""
import typing as t

import structlog
from pydantic import ValidationError
from sqlalchemy import select

from app_media.interfaces import AbstractMediaService
from app_media.models import Media
from app_media.schemas import MediaOrmSchema
from db import session
from exceptions import BackendException, ErrorsList, exc_handler
from settings import settings

logger = structlog.get_logger()


class MediaDbService(AbstractMediaService):
    """
    Класс реализует CRUID для медиа объектов в СУБД PostgreSql
    """

    @exc_handler(ConnectionRefusedError)
    async def get_media(self, media_id: int = None, hash: str = None) -> t.Optional[MediaOrmSchema]:
        """Метод возвращает pydantic-схему записи СУБД по идентификатору в СУБД или по хэшу файла.

        Parameters
        ----------

        media_id: int
            Идентификатор ресурса в СУБД.
        hash: str
            Хэш от файла.

        Returns
        -------
        MediaOrmSchema, optional
            Pydantic-схема ОРМ модели
        """

        logger.info("запрос медиа ресурса в Postgresql", media_id=media_id, hash=hash)
        if hash:
            query = select(Media).filter_by(hash=hash)
        elif media_id:
            query = select(Media).filter_by(id=media_id)
        else:
            logger.error(event="переданы неверные аргументы")
            raise BackendException(**ErrorsList.incorrect_parameters)
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().first():
                    try:
                        result = MediaOrmSchema.from_orm(result)
                    except ValidationError as e:
                        logger.exception(event="ошибка сериализации", exc_info=e)
                        raise BackendException(**ErrorsList.serialize_error)
                    else:
                        logger.info(event="возвращаем результат", result=result.dict())
                        return result
        logger.warning(event="не получилось")

    @exc_handler(ConnectionRefusedError)
    async def create_media(self, hash: str, file_name: str) -> t.Optional[MediaOrmSchema]:
        """
        Метод сохраняет данные о файле в СУБД.

        Parameters
        ----------
        hash: str
            Хэш от файла.
        file_name: str
            Имя файла.

        Returns
        -------
        MediaOrmSchema, optional
            Pydantic-схема ОРМ модели медиа ресурса.
        """
        media = Media(hash=hash, link=settings.media_url + "/" + file_name)
        logger.info(event="сохраняем медиа-объект в Postgresql", hash=hash, link=settings.media_url + "/" + file_name)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(media)
                await async_session.commit()
                try:
                    result = MediaOrmSchema.from_orm(media)
                except ValidationError as e:
                    logger.exception(event="ошибка сериализации", exc_info=e)
                    raise BackendException(**ErrorsList.serialize_error)
                else:
                    logger.info(event="возвращаем результат", result=result.dict())
                    return result
        logger.warning(event="не получилось")

    @exc_handler(ConnectionRefusedError)
    async def get_many_media(self, ids: t.List[int]) -> t.Optional[t.List[str]]:
        """
        Метод возвращает множество медиа-ресурсов по списку идентификаторов.

        Parameters
        ----------
        ids: List[int]
            Список идентификаторов ресурсов в СУБД.
        Returns
        -------
        List[str]
            Список URL адресов картинки
        """
        query = select(Media.link).filter(Media.id.in_(ids))
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().all():
                    logger.info(event="возвращаем результат", result=result)
                    return result
        logger.info(event="нет данных для возвращения")
