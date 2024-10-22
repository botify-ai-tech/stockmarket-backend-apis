import uuid
from datetime import datetime
# from ..db.base import Base
from server.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, JSON, DateTime, ARRAY, Boolean
from sqlalchemy.orm import relationship

class NewsItem(Base):

    # __tablename__ = "news_items"

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
    image = Column(String)

    created_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NewsSave(Base):

    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    news_id = Column(String, ForeignKey("news_items.id", ondelete="CASCADE"), index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    news = relationship("NewsItem")
    user = relationship("User")