from pydantic import BaseModel
from typing import Optional


class NewsSave(BaseModel):
    user_id: str
    news_id: str


class CreateNewsSave(NewsSave):
    pass


class UpdateNewsSave(NewsSave):
    pass
