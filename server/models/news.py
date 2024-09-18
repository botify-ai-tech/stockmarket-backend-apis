import uuid
from datetime import datetime
from server.db.base import Base
from sqlalchemy import Column, String, JSON, DateTime


class StockNews(Base):

    __tablename__ = "news_items"

    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_search = Column(String)
    title = Column(String)
    description = Column(String)
    time_to_out_news = Column(String)
    feed = Column(String)
    link = Column(String)
    similar = Column(JSON)

    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
