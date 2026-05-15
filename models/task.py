from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
from enums.task_enums import TaskCategory, TaskPriority
import uuid

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(SQLEnum(TaskCategory), nullable=False)
    priority = Column(SQLEnum(TaskPriority), nullable=False)
    target_duration = Column(Integer, nullable=False) # in minutes
    deadline = Column(DateTime, nullable=False)
    reminder_offset = Column(Integer, default=0) # in minutes before deadline
    
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="tasks")

    def __repr__(self):
        return f"<Task(title='{self.title}', category='{self.category}')>"
