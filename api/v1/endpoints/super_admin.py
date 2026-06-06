from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import UUID4
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from enums.member_enums import MemberRole
from enums.log_enums import LogEvent
from schemas.api_config import ApiConfigResponse, ApiConfigUpdateRequest
from schemas.super_admin import AdminCreateRequest, AdminResponse, AdminUpdateRequest
from services.log_service import log_user_action
from services.super_admin_service import (
    get_api_config_service,
    update_api_config_service,
    get_admins_service,
    create_admin_service,
    update_admin_service,
    delete_admin_service,
    export_db_to_csv_service,
)

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
    log_user_action(db, current_user, LogEvent.UPDATE, "Superadmin updated api config")
    return config


@router.get("/admins", response_model=List[AdminResponse])
def get_admins(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    return get_admins_service(db)


@router.post("/admins", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_admin(
    admin_in: AdminCreateRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    admin = create_admin_service(db, admin_in)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username atau email sudah terdaftar")
    log_user_action(db, current_user, LogEvent.CREATE, f"Superadmin created admin: {admin.username}")
    return admin


@router.put("/admins/{admin_id}", response_model=AdminResponse)
def update_admin(
    admin_id: UUID4,
    admin_in: AdminUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    admin = update_admin_service(db, admin_id, admin_in)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin tidak ditemukan")
    log_user_action(db, current_user, LogEvent.UPDATE, f"Superadmin updated admin {admin_id}")
    return admin


@router.delete("/admins/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    success = delete_admin_service(db, admin_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin tidak ditemukan")
    log_user_action(db, current_user, LogEvent.DELETE, f"Superadmin deleted admin {admin_id}")
    return None


@router.get("/export-db")
def export_database(
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user),
):
    if current_user.role != MemberRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya super admin yang dapat mengakses data ini")
    csv_zip = export_db_to_csv_service(db)
    return StreamingResponse(
        iter([csv_zip]),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=fokusin_export.zip"},
    )
