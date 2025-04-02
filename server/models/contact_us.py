import uuid
from datetime import datetime
from server.db.base_class import Base
from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Boolean

class ContactUs(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    full_name = Column(String,nullable=False)
    phone_number = Column(String,nullable=False)
    email = Column(String,nullable=False)
    message = Column(String,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)