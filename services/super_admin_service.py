import uuid
from typing import List

from pydantic import UUID4
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.exceptions import DatabaseOperationError
from enums.member_enums import MemberRole
from models.member import Member
from models.api_config import ApiConfig
from schemas.super_admin import AdminCreateRequest, AdminUpdateRequest
from schemas.api_config import ApiConfigUpdateRequest


def get_admins_service(db: Session) -> List[Member]:
    try:
        return db.query(Member).filter(Member.role == MemberRole.ADMIN).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil data admin") from e


def create_admin_service(db: Session, admin_in: AdminCreateRequest) -> Member | None:
    try:
        existing = db.query(Member).filter(
            Member.username == admin_in.username
        ).first()
        if existing:
            return None

        hasher = PasswordHash.recommended()
        hashed_password = hasher.hash(admin_in.password)

        db_admin = Member(
            fullname=admin_in.fullname,
            username=admin_in.username,
            email="admin@fokusin.com",
            password=hashed_password,
            role=MemberRole.ADMIN,
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal membuat admin baru") from e


def update_admin_service(db: Session, admin_id: UUID4, admin_in: AdminUpdateRequest) -> Member | None:
    try:
        db_admin = db.query(Member).filter(
            Member.user_id == admin_id, Member.role == MemberRole.ADMIN
        ).first()
        if not db_admin:
            return None

        update_data = admin_in.model_dump(exclude_unset=True, exclude={"password"})
        for field, value in update_data.items():
            setattr(db_admin, field, value)

        if admin_in.password is not None:
            hasher = PasswordHash.recommended()
            db_admin.password = hasher.hash(admin_in.password)

        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal memperbarui data admin") from e


def delete_admin_service(db: Session, admin_id: UUID4) -> bool:
    try:
        db_admin = db.query(Member).filter(
            Member.user_id == admin_id, Member.role == MemberRole.ADMIN
        ).first()
        if not db_admin:
            return False
        db.delete(db_admin)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal menghapus admin") from e


def get_api_config_service(db: Session) -> ApiConfig | None:
    try:
        return db.query(ApiConfig).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil konfigurasi API") from e


def update_api_config_service(db: Session, config_in: ApiConfigUpdateRequest) -> ApiConfig:
    try:
        config = db.query(ApiConfig).first()
        if config:
            config.api_base_url = config_in.api_base_url
            config.stress_threshold = config_in.stress_threshold
            config.stress_threshold_frequency = config_in.stress_threshold_frequency
        else:
            config = ApiConfig(
                api_base_url=config_in.api_base_url,
                stress_threshold=config_in.stress_threshold,
                stress_threshold_frequency=config_in.stress_threshold_frequency,
            )
            db.add(config)
        db.commit()
        db.refresh(config)
        return config
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal memperbarui konfigurasi API") from e
