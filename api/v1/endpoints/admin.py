from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from enums.member_enums import MemberRole
from schemas.admin import MahasiswaCreateByAdminRequest, StressHistoryAdminResponse, UserAdminResponse, AdminDashboardResponse, DailyStressTrendResponse
from services.admin_service import create_mahasiswa_by_admin_service, get_mahasiswa_users_service, get_mahasiswa_stress_history_service, get_admin_dashboard_data_service, get_admin_daily_stress_trend_service

router = APIRouter()

@router.post("/mahasiswa", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
def create_mahasiswa_by_admin(
    member_in: MahasiswaCreateByAdminRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    if current_user.role not in (MemberRole.ADMIN, MemberRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses data ini"
        )

    member = create_mahasiswa_by_admin_service(db, member_in)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username atau email sudah terdaftar"
        )
    return member


@router.get("/mahasiswa", response_model=List[UserAdminResponse])
def get_mahasiswa_users(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    if current_user.role not in (MemberRole.ADMIN, MemberRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses data ini"
        )

    return get_mahasiswa_users_service(db)


@router.get("/stress-analysis/{user_id}", response_model=StressHistoryAdminResponse)
def get_mahasiswa_stress_history(
    user_id: UUID4,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    if current_user.role not in (MemberRole.ADMIN, MemberRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses data ini"
        )

    skip = (page - 1) * size
    items, total = get_mahasiswa_stress_history_service(db, user_id, skip, size)

    return StressHistoryAdminResponse(items=items, total=total, page=page, size=size)


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    if current_user.role not in (MemberRole.ADMIN, MemberRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses data ini"
        )

    return get_admin_dashboard_data_service(db)


@router.get("/dashboard/stress-trend", response_model=DailyStressTrendResponse)
def get_admin_dashboard_stress_trend(
    period: str = Query("this_month", description="Select 'this_month' for the last 30 days, or 'last_month' for the 30 days prior."),
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    if current_user.role not in (MemberRole.ADMIN, MemberRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses data ini"
        )
        
    if period not in ["this_month", "last_month"]:
        raise HTTPException(status_code=400, detail="Invalid period. Use 'this_month' or 'last_month'.")

    return get_admin_daily_stress_trend_service(db, period)
