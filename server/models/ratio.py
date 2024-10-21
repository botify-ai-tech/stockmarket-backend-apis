import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from server.db.base_class import Base


class Ratio(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    nifty_sahre = Column(String)
    stock_name = Column(String)
    favourable_indicators = Column(JSON)
    unfavourable_indicators = Column(JSON)
    summary = Column(String)
    pros = Column(JSON)
    cons = Column(JSON)
    investment_recommendation = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

