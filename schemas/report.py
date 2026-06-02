from pydantic import BaseModel

from schemas.stress_analysis import StressAnalysisResponse

class StressTrendResponse(BaseModel):
    labels: list[str]
    values: list[float]

class StressReportResponse(BaseModel):
    all_stress_analysis: list[StressAnalysisResponse]
    potential_stress_factors: dict