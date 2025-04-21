import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String

from server.db.base_class import Base


class NewsLetter(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    email = Column(String, nullable=True , unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

