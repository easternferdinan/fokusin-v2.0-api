from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
import uuid

class StressAnalysis(Base):
    __tablename__ = "stress_analysis"

    analysis_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=False)
    
    self_esteem = Column(Integer, nullable=False)
    depression = Column(Integer, nullable=False)
    headache = Column(Integer, nullable=False)
    sleep_quality = Column(Integer, nullable=False)
    study_load = Column(Integer, nullable=False)
    stress_level = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="stress_analyses")

    def __repr__(self):
        return f"<StressAnalysis(stress_level='{self.stress_level}', created_at='{self.created_at}')>"