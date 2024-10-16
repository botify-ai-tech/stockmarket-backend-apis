from typing import List, Optional, TypeVar
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.news import NewsItem
from server.schemas.news import CreateNews, UpdateNews

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

last_24_hours = datetime.now() - timedelta(hours=24)
cutoff_time = datetime.now() - timedelta(hours=48)


class CRUDNEWS(CRUDBase[NewsItem, CreateNews, UpdateNews]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateNews) -> NewsItem:
        return super().create(db, obj_in=obj_in)

    def get_by_id(self, db: Session, *, id: str) -> NewsItem:
        return db.query(NewsItem).filter(NewsItem.id == id).first()

    def update(self, db: Session, *, db_obj: NewsItem, obj_in: UpdateNews) -> NewsItem:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def get_new_search_query(self, db: Session, search: str, sector: str) -> NewsItem:
        return (
            db.query(NewsItem)
            .filter(
                and_(
                    NewsItem.created_at >= last_24_hours,
                    or_(
                        NewsItem.company_name.ilike(f"%{search}%"),
                        NewsItem.sectors.any(sector)  
                    ),
                )
            )
            .all()
        )

    def get_new_without_search_query(self, db: Session) -> NewsItem:
        return db.query(NewsItem).filter(NewsItem.created_at >= last_24_hours).all()
    
    def saved_news(self, db: Session, news_ids: list[int]) -> list[NewsItem]:
        return db.query(NewsItem).filter(NewsItem.id.in_(news_ids)).all()

    def get_48_old_news(self, db: Session) -> NewsItem:
        db.query(NewsItem).filter(NewsItem.created_at < cutoff_time).all()

    def remove(self, db: Session) -> Optional[NewsItem]:
        return super().remove_all(db)



news = CRUDNEWS(NewsItem)
