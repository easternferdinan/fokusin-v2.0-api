from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid

from db.session import Base
from enums.log_enums import LogLevel

class Log(Base):
    __tablename__ = "logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=True)
    
    level = Column(SQLEnum(LogLevel), nullable=False, default=LogLevel.INFO)
    event_type = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    extra_data = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="logs")

    @property
    def username(self):
        return self.member.username if self.member else None

    def __repr__(self):
        return f"<Log(event_type='{self.event_type}', level='{self.level}', created_at='{self.created_at}')>"
