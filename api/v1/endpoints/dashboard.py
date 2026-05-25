from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.member import Member
from schemas.dashboard import DashboardResponse
from services.dashboard_service import get_dashboard_data_service

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Retrieve all data for the dashboard for the current user.
    """
    return get_dashboard_data_service(db, current_user.user_id)