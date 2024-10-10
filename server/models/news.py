import uuid
from datetime import datetime
from ..db.base import Base
from sqlalchemy import Column, String, JSON, DateTime, ARRAY


class StockNews(Base):

    __tablename__ = "news_items"

    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    title = Column(String)
    published_date = Column(String)
    summary = Column(String)
    classification = Column(String)
    type_of_impact = Column(String)
    description = Column(String)
    sectors = Column(ARRAY(String))
    category = Column(String)
    Country = Column(String)
    company_name = Column(String)
    stock_name = Column(ARRAY(String))
    scale_of_impact = Column(String)
    timeframe_of_impact = Column(String)
    investor_sentiment = Column(String)
    market_volatility = Column(String)
    detailed_explanation = Column(ARRAY(String))
    time_to_out_news = Column(String)
    feed = Column(String)
    other_news_link = Column(String)
    similar = Column(JSON)

    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
