from typing import Optional
from pydantic import BaseModel


class ChatBase(BaseModel):
    id: str = None
    user_id: str = None
    session_id: Optional[str] = None
    question: Optional[str]  = None
    answer: Optional[str] = None
    filename: Optional[str] = None
    url: Optional[str] = None
    content_topic: Optional[str] = None
    is_deleted: Optional[bool] = False


class CreateChat(ChatBase):
    pass


class UpdateChat(ChatBase):
    pass


class Query(BaseModel):
    question: str

class ChatHistory(BaseModel):
    session_id: Optional[str]