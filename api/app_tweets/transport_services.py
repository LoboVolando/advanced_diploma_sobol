import typing as t
from abc import ABC, abstractmethod

from .schemas import TweetBaseSchema


class AbstractTweetService(ABC):
    """адстрактный класс для работы с сервисом твиттов"""

    @abstractmethod
    def get_list(self) -> t.Optional[t.List[TweetBaseSchema]]:
        """
        метод получения списка твитов
        :return: опциональный список твиттов
        """
        ...


class TweetMockService(AbstractTweetService):

    def get_list(self) -> t.Optional[t.List[TweetBaseSchema]]:
        return [
            TweetBaseSchema(content="tweet-1"),
            TweetBaseSchema(content="tweet-2"),
        ]
