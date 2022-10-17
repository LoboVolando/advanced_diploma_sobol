"""
interfaces.py
-------------
Модуль определяет абстрактные классы для реализации сервисов уровня базы данных.
Это позволяет реализовать механизмы взаимодействия с разными СУБД, не меняя саму бизнес-логику приложения.
"""

import typing as t
from abc import ABC, abstractmethod

from app_users.models import Author
from app_users.schemas import *
from schemas import SuccessSchema
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractAuthorService(ABC):
    """Класс инкапсулирует методы для работы с авторами твитов."""

    @abstractmethod
    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> AuthorProfileApiSchema:
        """Абстрактный метод получения автора по одному из параметров.

        Parameters
        ----------
        api_key: str
            Уникальный ключ фронтенда.
        author_id: int
            Идентификатор автора в СУБД.
        name: str
            Имя автора.
        """
        ...

    @abstractmethod
    async def create_author(self, name: str, api_key: str, password: str) -> t.Optional[Author]:
        """Абстрактный метод создания автора

        Parameters
        ----------
        name: str
            Имя нового автора.
        api_key: str
            Уникальный ключ для фронтенда.
        password: str
            Зашифрованный пароль нового автора.
        """
        ...

    @abstractmethod
    async def update_follow(
        self,
        reading_author: AuthorBaseSchema,
        writing_author: AuthorBaseSchema,
        followers: dict,
        following: dict,
    ) -> SuccessSchema:
        """Адстрактный метод создаёт связи между читающим и пишущим авторами.

        Parameters
        ----------
        reading_author: ProfileAuthorSchema
            Профиль читающего автора.
        writing_author: ProfileAuthorSchema
            Профиль пишущего автора.
        followers: dict
            Словарь всех писателей пользователя.
        following: dict
            Сроварь всех читателей пользователя.
        """
        ...
