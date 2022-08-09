from abc import ABC, abstractmethod


class AbstractAuthorService(ABC):
    @abstractmethod
    async def me(self, api_key: str):
        """абстрактный метод получения автора по ключу"""
        ...

    @abstractmethod
    async def get_author_by_id(self, author_id: int):
        """абстрактный метод получения автора по id"""
        ...

    @abstractmethod
    async def add_follow(self, author_id: int, follow_id: int):
        """абстрактный метод фаллования автора по id"""
        ...

    @abstractmethod
    async def remove_follow(self, author_id: int, follow_id: int):
        """абстрактный метод расфаллования автора по id"""
        ...

    @abstractmethod
    async def error_get_user(self):
        """генерация ошибки получения юзера для фронта"""
        ...
