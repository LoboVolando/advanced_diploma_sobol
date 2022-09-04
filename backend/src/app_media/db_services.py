"""
db_services.py
--------------
Модуль реализует классы для взаимодействия между бизнес-логикой и СУБД.
"""
import typing as t

from loguru import logger
from sqlalchemy import select

from app_media.models import Media
from app_media.schemas import MediaOrmSchema
from app_media.interfaces import AbstractMediaService
from db import session


class MediaDbService(AbstractMediaService):
    """
    Класс реализует CRUID для медиа объектов в СУБД PostgreSql
    """

    @staticmethod
    async def get_media(media_id: int = None, hash: str = None) -> t.Optional[MediaOrmSchema]:
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

        logger.info("запрос медиа ресурса...")
        if hash:
            query = select(Media).filter_by(hash=hash)
        elif media_id:
            query = select(Media).filter_by(id=media_id)
        else:
            return
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().first():
                    return MediaOrmSchema.from_orm(result)

    @staticmethod
    async def create_media(hash: str, file_name: str) -> t.Optional[MediaOrmSchema]:
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
        media = Media(hash=hash, link="static/" + file_name)
        async with session() as async_session:
            async with async_session.begin():
                async_session.add(media)
                await async_session.commit()
                return MediaOrmSchema.from_orm(media)

    @staticmethod
    async def get_many_media(ids: t.List[int]):
        """
        Метод возвращает множество медиа-ресурсов по списку идентификаторов.

        Parameters
        ----------
        ids: List[int]
            Список идентификаторов ресурсов в СУБД.
        Returns
        -------
        ???
        """
        query = select(Media.link).filter(Media.id.in_(ids))
        async with session() as async_session:
            async with async_session.begin():
                qs = await async_session.execute(query)
                if result := qs.scalars().all():
                    return result
