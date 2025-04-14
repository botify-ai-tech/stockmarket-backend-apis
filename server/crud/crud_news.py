from typing import List, Optional, TypeVar
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.news import NewsItem
from server.schemas.news import CreateNews, UpdateNews
import pytz

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

last_24_hours = datetime.now() - timedelta(hours=24)
cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=48)


class CRUDNEWS(CRUDBase[NewsItem, CreateNews, UpdateNews]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateNews) -> NewsItem:
        return super().create(db, obj_in=obj_in)

    def get_by_id(self, db: Session, *, id: str) -> NewsItem:
        return db.query(NewsItem).filter(NewsItem.id == id).first()

    def update(self, db: Session, *, db_obj: NewsItem, obj_in: UpdateNews) -> NewsItem:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def _get_time_bounds(self):
        now = datetime.now(pytz.UTC)
        return now - timedelta(hours=24), now - timedelta(hours=48)

    def get_new_search_query(self, db: Session, search: str, skip: int = 0, limit: int = 10) -> NewsItem:
        last_24, last_48 = self._get_time_bounds()

        search_filter = or_(
            NewsItem.company_name.ilike(f"%{search}%"),
            NewsItem.sectors.any(search),
        )

        base_filter = lambda time: and_(
            NewsItem.created_at >= time,
            or_(
                NewsItem.company_name.ilike(f"%{search}%"),
                NewsItem.sectors.any(search),
            )
        )

        news_24 = db.query(NewsItem).filter(base_filter(last_24)).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()
        if news_24:
            return news_24

        news_48 = db.query(NewsItem).filter(base_filter(last_48)).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()
        if news_48:
            return news_48

        # fallback to latest 20 items regardless of time
        return db.query(NewsItem).filter(search_filter).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()        
    
    def get_total_new_search_query(self, db: Session, search: str) -> NewsItem:
        last_24, last_48 = self._get_time_bounds()

        base_filter = lambda time: and_(
            NewsItem.created_at >= time,
            or_(
                NewsItem.company_name.ilike(f"%{search}%"),
                NewsItem.sectors.any(search),
            )
        )

        count_24 = db.query(NewsItem).filter(base_filter(last_24)).count()
        if count_24:
            return count_24

        count_48 = db.query(NewsItem).filter(base_filter(last_48)).count()
        if count_48:
            return count_48

        # fallback to total count of recent 20 news items for search
        return db.query(NewsItem).filter(
            or_(
                NewsItem.company_name.ilike(f"%{search}%"),
                NewsItem.sectors.any(search),
            )
        ).count()

    def get_new_without_search_query(self, db: Session, skip: int = 0, limit: int = 10) -> NewsItem:
        last_24, last_48 = self._get_time_bounds()

        news_24 = db.query(NewsItem).filter(NewsItem.created_at >= last_24).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()
        if news_24:
            return news_24

        news_48 = db.query(NewsItem).filter(NewsItem.created_at >= last_48).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()
        if news_48:
            return news_48

        # fallback to latest 20 news
        return db.query(NewsItem).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()

    def get_total_news_without_search_query(self, db: Session) -> NewsItem:
        last_24, last_48 = self._get_time_bounds()

        count_24 = db.query(NewsItem).filter(NewsItem.created_at >= last_24).count()
        if count_24:
            return count_24

        count_48 = db.query(NewsItem).filter(NewsItem.created_at >= last_48).count()
        if count_48:
            return count_48

        return db.query(NewsItem).count()

    def saved_news(self, db: Session, news_ids: list[int]) -> list[NewsItem]:
        query = db.query(NewsItem).filter(NewsItem.id.in_(news_ids)).all()
        return query

    def get_48_old_news(self, db: Session) -> NewsItem:
        return db.query(NewsItem).filter(NewsItem.created_at < cutoff_time).all()

    def remove(self, db: Session, id: str) -> Optional[NewsItem]:
        return super().remove(db, id=id)


news = CRUDNEWS(NewsItem)
