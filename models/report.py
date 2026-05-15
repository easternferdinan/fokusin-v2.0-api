from sqlalchemy import Column, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from db.session import Base
import uuid

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("members.user_id"), nullable=False)
    
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # CLARIFY: what are the types? can it be in enum?
    period = Column(String, nullable=False)
    content = Column(String, nullable=False)
    description = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    generated_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    member = relationship("Member", back_populates="reports")

    def __repr__(self):
        return f"<Report(title='{self.title}', period='{self.period}')>"