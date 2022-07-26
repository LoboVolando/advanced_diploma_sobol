from pydantic import BaseModel, Field


class TweetBaseSchema(BaseModel):
    content: str = Field(example="запомните этот твит")
