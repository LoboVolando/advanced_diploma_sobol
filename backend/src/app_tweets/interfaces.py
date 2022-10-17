"""
interfaces.py
-------------
Модуль определяет абстрактные классы для реализации сервисов уровня базы данных.
Это позволяет реализовать механизмы взаимодействия с разными СУБД, не меняя саму бизнес-логику приложения.
"""
import typing as t
from abc import ABC, abstractmethod

from app_tweets.schemas import TweetInSchema, TweetSchema, TweetModelSchema
from schemas import SuccessSchema


class AbstractTweetService(ABC):
    """Абстрактный класс инкапсулирует cruid-методы для твитов в СУБД."""

    @abstractmethod
    def get_list(self, author_id: int) -> t.List[TweetModelSchema]:
        """Абстрактный метод получения списка твитов для конкретного автора.

        Parameters
        ----------
        author_id: int
            Идентификатор автора.
        """
        ...

    @abstractmethod
    def create_tweet(
        self,
        new_tweet: TweetInSchema,
        author_id: int,
        attachments: t.Optional[t.List[str]],
    ):
        """
        Абстрактный метод сохранения твита.

        Parameters
        ----------
        new_tweet: TweetInSchema
            Входящая pydantic-схема с новым твитом от фронтенда.
        author_id: int
            Идентификатор автора в СУБД.
        attachments: t.List[str], optional
            Список ссылок на картинки.
        """
        ...

    @abstractmethod
    def delete_tweet(self, tweet_id: int, author_id: int):
        """Абстрактный метод удаляет твит по идентификатору СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        author_id: int
            Идентификатор автора в СУБД.

        Note
        ----
        Имеется в виду мягкое удаление через флаг удаления. На самом деле твит остаётся для принятия решения о
        возбуждении уголовного дела по 288 статье УК РФ.
        """
        ...

    @abstractmethod
    async def get_tweet_by_id(self, tweet_id: int) -> t.Optional[TweetModelSchema]:
        """Абстрактный метод возвращает твит по идентификатору СУБД.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.

        Returns
        -------
        TweetSchema
            Pydantic-схема твита.
        """
        ...

    @abstractmethod
    async def update_like_in_tweet(self, tweet_id: int, likes: dict) -> SuccessSchema:
        """Абстрактный метод перезаписывает лайки в СУБД у конкретного твита.

        Parameters
        ----------
        tweet_id: int
            Идентификатор твита в СУБД.
        likes: dict
            Обновлённый набор лайков.
        """
        ...
