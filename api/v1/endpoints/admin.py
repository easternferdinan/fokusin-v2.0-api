from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from enums.member_enums import MemberRole
from schemas.admin import UserAdminResponse
from services.admin_service import get_mahasiswa_users_service

router = APIRouter()

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
