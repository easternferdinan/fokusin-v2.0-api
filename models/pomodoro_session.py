from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, UUID, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
from enums.pomodoro_enums import PomodoroStatus
import uuid

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    pomodoro_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=False)
    
    title = Column(String, nullable=False)
    status = Column(SQLEnum(PomodoroStatus), nullable=False, default=PomodoroStatus.ACTIVE)
    
    session_start = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    session_end = Column(DateTime, nullable=True)
    
    elapsed_time = Column(Integer, default=0) # in seconds
    duration = Column(Integer, nullable=False) # intended duration in minutes
    break_duration = Column(Integer, nullable=False) # in minutes
    
    completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="pomodoro_sessions")

    def __repr__(self):
        return f"<PomodoroSession(title='{self.title}', status='{self.status}')>"
