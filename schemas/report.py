from pydantic import BaseModel

from schemas.stress_analysis import StressAnalysisResponse

class StressTrendResponse(BaseModel):
    labels: list[str]
    values: list[float]

class PotentialStressFactorsResponse(BaseModel):
    deadline_is_tomorrow_tasks: str
    piling_up_tasks: str
    sleep_quality: str

class StressReportResponse(BaseModel):
    all_stress_analysis: list[StressAnalysisResponse]
    potential_stress_factors: PotentialStressFactorsResponse