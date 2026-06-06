from sqlalchemy import Column, String, DateTime, Enum, UUID, SmallInteger
from datetime import datetime, UTC
from db.session import Base
from enums.stress_level import StressLevelEnum
import uuid

class ApiConfig(Base):
    __tablename__ = "api_config"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    api_base_url = Column(String, nullable=False)
    stress_threshold = Column(Enum(StressLevelEnum), nullable=False, default=StressLevelEnum.TINGGI)
    stress_threshold_frequency = Column(SmallInteger, nullable=False, default=3)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<ApiConfig(id='{self.id}', api_base_url='{self.api_base_url}')>"
