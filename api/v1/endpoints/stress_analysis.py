from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from schemas.stress_analysis import StressAnalysisCreateRequest, StressAnalysisResponse, StressAnalysisRequirementsStatusResponse
from services.stress_analysis_service import (
    get_latest_stress_analysis_service,
    check_stress_analysis_requirements_service,
    create_stress_analysis_service,
    get_all_stress_analysis_service,
)

router = APIRouter()

@router.get("/", response_model=List[StressAnalysisResponse])
def get_stress_analysis_data(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve all stress analysis data for the current user.
    """
    return get_all_stress_analysis_service(db, current_user.user_id)

@router.get("/latest", response_model=StressAnalysisResponse)
def get_latest_stress_analysis(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve the latest stress analysis result for the current user.
    """
    analysis = get_latest_stress_analysis_service(db, current_user.user_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stress analysis found for this user."
        )
    return analysis

@router.get("/requirements-status", response_model=StressAnalysisRequirementsStatusResponse)
def get_stress_analysis_requirements_status(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve status of requirements to generate stress analysis report.
    """
    return check_stress_analysis_requirements_service(db, current_user.user_id)

@router.post("/", response_model=StressAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_stress_analysis(
    analysis_in: StressAnalysisCreateRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Perform a new stress analysis for the current user.
    """
    return create_stress_analysis_service(db, analysis_in, current_user.user_id)

@router.get("/history", response_model=List[StressAnalysisResponse])
def get_stress_analysis_history(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve all stress analysis history for the current user.
    """
    return get_all_stress_analysis_service(db, current_user.user_id)