import typing as t
from abc import ABC, abstractmethod
from .schemas import ProfileAuthorSchema, SuccessSchema
from .models import Author

class AbstractAuthorService(ABC):
    @abstractmethod
    async def me(self, api_key: str) -> ProfileAuthorSchema:
        """абстрактный метод получения автора по ключу"""
        ...

    @abstractmethod
    async def get_author(self, author_id: int = None, api_key: str = None, name: str = None) -> ProfileAuthorSchema:
        """абстрактный метод получения автора по id"""
        ...

    @abstractmethod
    async def create_author(self, name: str, api_key: str, password: str) -> t.Optional[Author]:
        """абстрактный метод создания автора"""
        ...

    @abstractmethod
    async def update_follow(
            self,
            reading_author: ProfileAuthorSchema,
            writing_author: ProfileAuthorSchema,
            followers: dict,
            following: dict,
    ) -> SuccessSchema:
        """Адстрактный метод обновления фоловеров у автора."""
