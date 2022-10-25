"""
interfaces.py
-------------
Модуль определяет абстрактные классы для реализации сервисов уровня базы данных.
Это позволяет реализовать механизмы взаимодействия с разными СУБД, не меняя саму бизнес-логику приложения.
"""
import typing as t
from abc import ABC, abstractmethod

from app_media.schemas import MediaOrmSchema


class AbstractMediaService(ABC):
    """Абстрактный класс инкапсулирует cruid-методы для медиа ресурсов в СУБД."""

    @abstractmethod
    async def get_media(self, media_id: int = None, hash: str = None) -> t.Optional[MediaOrmSchema]:
        """Абстрактный метод возвращает pydantic-схему записи СУБД
        по идентификатору в СУБД или по хэшу файла.

        Parameters
        ----------
        media_id: int
            Идентификатор ресурса в СУБД.
        hash: str
            Хэш от файла.
        """
        ...

    @abstractmethod
    async def create_media(self, hash: str, file_name: str) -> t.Optional[MediaOrmSchema]:
        """Абстрактный метод сохраняет данные о файле в СУБД.

        Parameters
        ----------
        hash: str
            Хэш от файла.
        file_name: str
            Имя файла.
        """
        ...

    @abstractmethod
    async def get_many_media(self, ids: t.List[int]) -> t.Optional[t.List[str]]:
        """Абстрактный метод возвращает множество медиа-ресурсов по списку идентификаторов.

        Parameters
        ----------
        ids: List[int]
            Список идентификаторов ресурсов в СУБД.
        Returns
        -------
        links: List[str]
            Список URL адресов картинки
        """
        ...
