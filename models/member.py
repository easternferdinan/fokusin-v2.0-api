from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, UUID, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
from enums.member_enums import MemberRole
import uuid

class Member(Base):
    __tablename__ = "members"

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    fullname = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Hash
    role = Column(SQLEnum(MemberRole), nullable=False, default=MemberRole.USER)
    
    mental_health_history = Column(Boolean, nullable=False)
    academic_performance = Column(Integer, nullable=False)
    social_support = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    pomodoro_sessions = relationship("PomodoroSession", back_populates="member", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="member", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="member", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="member", cascade="all, delete-orphan")
    stress_analyses = relationship("StressAnalysis", back_populates="member", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(username='{self.username}', email='{self.email}')>"
