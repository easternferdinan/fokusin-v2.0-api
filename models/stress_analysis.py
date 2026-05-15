from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
import uuid

class StressAnalysis(Base):
    __tablename__ = "stress_analysis"

    analysis_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("members.user_id"), nullable=False)
    
    self_esteem = Column(Integer, nullable=False)
    mental_health_history = Column(Boolean, nullable=False)
    depression = Column(Integer, nullable=False)
    headache = Column(Integer, nullable=False)
    sleep_quality = Column(Integer, nullable=False)
    academic_performance = Column(Integer, nullable=False)
    study_load = Column(Integer, nullable=False)
    social_support = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="stress_analyses")

    def __repr__(self):
        return f"<StressAnalysis(stress_level='{self.stress_level}', created_at='{self.created_at}')>"