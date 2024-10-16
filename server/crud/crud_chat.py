from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.chat import Chat
from server.schemas.chat import CreateChat, UpdateChat

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDCHAT(CRUDBase[Chat, CreateChat, UpdateChat]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateChat) -> Chat:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Chat, obj_in: UpdateChat) -> Chat:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Chat]:
        return super().remove(db, id=id)
    
    def get_chat_history(self, db:Session, id: str) -> Chat:
        return db.query(Chat).filter(Chat.user_id == id).all()


chat = CRUDCHAT(Chat)
