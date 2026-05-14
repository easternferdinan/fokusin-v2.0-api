from pydantic import BaseModel
from datetime import datetime

# CLARIFY: How is the report going to be presented to the user?
# How will it be generated? Why store the file name?
# CLARIFY: What are the actions that can be performed on a report?
class ReportBase(BaseModel):
    title: str
    report_type: str # TODO: enum?
    period: str
    content: str
    description: str
    file_name: str
    generated_at: datetime
    created_at: datetime
    updated_at: datetime

class ReportResponse(ReportBase):
    report_id: str