from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
from enums.member_enums import MemberRole
import uuid

class Member(Base):
    __tablename__ = "members"

    user_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    fullname = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Hash
    role = Column(SQLEnum(MemberRole), nullable=False, default=MemberRole.USER)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pomodoro_sessions = relationship("PomodoroSession", back_populates="member", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="member", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="member", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="member", cascade="all, delete-orphan")
    stress_analyses = relationship("StressAnalysis", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(username='{self.username}', email='{self.email}')>"
