from pydantic import BaseModel


class ChatBase(BaseModel):
    id: str = None
    user_id: str = None
    question: str  = None
    answer: str = None
    is_deleted: bool = False


class CreateChat(ChatBase):
    pass


class UpdateChat(ChatBase):
    pass


class Query(BaseModel):
    question: str