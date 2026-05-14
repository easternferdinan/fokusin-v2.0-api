from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base
import uuid

class StressAnalysis(Base):
    __tablename__ = "stress_analysis"

    analysis_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("members.user_id"), nullable=False)
    
    self_esteem = Column(int, nullable=False)
    mental_health_history = Column(bool, nullable=False)
    depression = Column(int, nullable=False)
    headache = Column(int, nullable=False)
    sleep_quality = Column(int, nullable=False)
    academic_performance = Column(int, nullable=False)
    study_load = Column(int, nullable=False)
    social_support = Column(int, nullable=False)
    stress_level = Column(int, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="stress_analyses")

    def __repr__(self):
        return f"<StressAnalysis(stress_level='{self.stress_level}', detected_at='{self.detected_at}')>"