import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from server.db.base_class import Base


class Contact(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    name = Column(String)
    email = Column(String, nullable=True)
    phone_number = Column(String)
    message = Column(String(length=1000))
    

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")