from pydantic import BaseModel, UUID4
from datetime import datetime

# CLARIFY: How will it be generated? Why store the file name?
class ReportBase(BaseModel):
    title: str
    report_type: str # CLARIFY: what are the types? can it be in enum?
    period: str
    content: str
    description: str

class ReportResponse(ReportBase):
    report_id: UUID4
    file_name: str
    generated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReportCreateRequest(ReportBase):
    pass