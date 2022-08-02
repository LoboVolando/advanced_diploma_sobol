from abc import ABC, abstractmethod

from .schemas import SuccessSchema, TweetInSchema, TweetSchema


class AbstractTweetService(ABC):
    """адстрактный класс для работы с сервисом твиттов"""

    @abstractmethod
    def get_list(self, api_key: str):
        """
        метод получения списка твитов
        :return: опциональный список твиттов
        """
        ...

    @abstractmethod
    def create_tweet(self, new_tweet: TweetInSchema, author_id: int):
        """абстрактный метод сохранения твита"""
        ...

    @abstractmethod
    def delete_tweet(self, tweet_id: int, author_id: int):
        ...

    @abstractmethod
    async def get_tweet_by_id(self, tweet_id: int) -> TweetSchema:
        ...

    @abstractmethod
    async def add_like_to_tweet(
        self, tweet_id: int, author_id: int
    ) -> SuccessSchema:
        ...

    @abstractmethod
    async def remove_like_from_tweet(
        self, tweet_id: int, author_id: int
    ) -> SuccessSchema:
        ...
