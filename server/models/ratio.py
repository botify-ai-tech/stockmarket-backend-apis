import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from server.db.base_class import Base


class Ratio(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    nifty_sahre = Column(String)
    financial_ratio_analysis = Column(JSON)
    key_highlights = Column(JSON)
    stock_value = Column(JSON)
    conclusion = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
