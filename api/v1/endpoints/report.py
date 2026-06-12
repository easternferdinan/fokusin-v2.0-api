from api.v1.endpoints.stress_analysis import router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.member import Member
from schemas.report import StressTrendResponse, StressReportResponse
from services.report_service import get_stress_report_service, get_stress_trend_service

router = APIRouter()

@router.get("/", response_model=StressReportResponse)
def get_stress_report(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve stress analysis report for the current user.

    This includes:
    - All stress analysis data
    - Potential stress factors data
    """
    return get_stress_report_service(db, current_user.user_id)

@router.get("/stress-trend", response_model=StressTrendResponse)
def get_stress_trend(
    period: str, # 'harian', 'mingguan', 'bulanan'
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve stress trend data for graphing.
    """
    if period not in ['harian', 'mingguan', 'bulanan']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid period. Must be one of 'harian', 'mingguan', 'bulanan'."
        )
    return get_stress_trend_service(db, current_user.user_id, period)
