import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Integer

from server.db.base_class import Base
class BugReport(Base):
    __tablename__ = 'bug_reports'
    
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    photo = Column(String(255), nullable=True)  # Stores file path or URL to the photo
    full_name = Column(String(100), nullable=True)
    message = Column(Text, nullable=True)  # Making message required
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
