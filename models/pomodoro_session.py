from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
import uuid

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    pomodoro_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("members.user_id"), nullable=False)
    
    title = Column(String, nullable=False)
    status = Column(String, nullable=False) # CLARIFY: what are the statuses? e.g. started, completed, interrupted
    
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=False)
    
    elapsed_time = Column(Integer, nullable=False) # in seconds
    duration = Column(Integer, nullable=False) # intended duration in minutes
    break_duration = Column(Integer, default=5) # in minutes
    
    completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="pomodoro_sessions")

    def __repr__(self):
        return f"<PomodoroSession(title='{self.title}', status='{self.status}')>"
