import typing as t

from .schemas import TweetBaseSchema
from .transport_services import AbstractTweetService

class TweetService:
    """
    бизнес-логика работы с твиттами
    """

    def __init__(self, service: AbstractTweetService):
        self.service = service

    def get_list(self) -> t.Optional[t.List[TweetBaseSchema]]:
        return self.service.get_list()
