from typing import List, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.news import NewsSave
from server.schemas.news_save import CreateNewsSave, UpdateNewsSave

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDNEWSSAVE(CRUDBase[NewsSave, CreateNewsSave, UpdateNewsSave]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateNewsSave) -> NewsSave:
        return super().create(db, obj_in=obj_in)
    
    def get_all_news(self, db: Session, *, user_id: str, news_id: str) -> NewsSave:
        return db.query(NewsSave).filter(NewsSave.user_id == user_id, NewsSave.news_id == news_id).all()
    
    def update(self, db: Session, *, db_obj: NewsSave, obj_in: UpdateNewsSave) -> NewsSave:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)
    
    def get_news_id(self, db: Session, user_id: str) -> NewsSave:
        return db.query(NewsSave).filter(NewsSave.user_id == user_id).all()
    
    def existing_save(self, db: Session, user_id: str, news_id: str) -> NewsSave:
        return db.query(NewsSave).filter(NewsSave.user_id == user_id, NewsSave.news_id == news_id).first()
    
    def remove(self, db: Session, *, id: str) -> Optional[NewsSave]:
        return super().remove(db, id=id)
    
    def get_save_news_id(self, db: Session) -> NewsSave:
        return db.query(NewsSave.news_id).distinct().all()
    
news_save = CRUDNEWSSAVE(NewsSave)