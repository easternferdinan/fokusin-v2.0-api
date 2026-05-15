from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
import uuid

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=False)
    
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(message='{self.message}', is_read={self.is_read})>"