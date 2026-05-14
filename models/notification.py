from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
import uuid

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("members.user_id"), nullable=False)
    
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(message='{self.message}', is_read={self.is_read})>"