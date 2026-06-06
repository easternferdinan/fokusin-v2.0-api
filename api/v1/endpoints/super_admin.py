from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from models.member import Member
from enums.member_enums import MemberRole
from schemas.api_config import ApiConfigResponse, ApiConfigUpdateRequest
from services.api_config_service import get_api_config_service, update_api_config_service

router = APIRouter()

@router.get("/config", response_model=ApiConfigResponse)
def get_api_config(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    config = get_api_config_service(db)
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konfigurasi API tidak ditemukan")
    return config

@router.put("/config", response_model=ApiConfigResponse)
def update_api_config(
    config_in: ApiConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    config = update_api_config_service(db, config_in)
    return config
