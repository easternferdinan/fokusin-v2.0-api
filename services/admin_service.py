import uuid
from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from pwdlib import PasswordHash

from core.exceptions import DatabaseOperationError
from enums.member_enums import MemberRole
from models.member import Member
from models.stress_analysis import StressAnalysis
from schemas.admin import MahasiswaCreateByAdminRequest

def get_mahasiswa_users_service(db: Session) -> List[Member]:
    try:
        # Correlated subquery: fetch the latest stress_level for each user
        # from stress_analysis, ordered by created_at descending, limited to 1
        latest_stress_subq = (
            select(StressAnalysis.stress_level)
            .where(StressAnalysis.user_id == Member.user_id)
            .order_by(StressAnalysis.created_at.desc())
            .limit(1)
            .correlate(Member)
            .scalar_subquery()
        )

        results = db.query(
            Member,
            latest_stress_subq.label('latest_stress_level')
        ).filter(
            Member.role == MemberRole.MAHASISWA
        ).order_by(
            Member.fullname.asc()
        ).all()

        # Attach the latest stress level onto each Member object
        # so Pydantic can pick it up via from_attributes
        members = []
        for member, stress_level in results:
            member.latest_stress_level = stress_level
            members.append(member)

        return members
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil data mahasiswa") from e


def get_mahasiswa_stress_history_service(
    db: Session, user_id: uuid.UUID, skip: int, limit: int
) -> Tuple[List[StressAnalysis], int]:
    try:
        query = db.query(StressAnalysis).filter(StressAnalysis.user_id == user_id)

        total = query.count()

        items = query.order_by(StressAnalysis.created_at.desc()).offset(skip).limit(limit).all()

        return items, total
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil riwayat stress analysis") from e


def create_mahasiswa_by_admin_service(
    db: Session, member_in: MahasiswaCreateByAdminRequest
) -> Member | None:
    try:
        existing = db.query(Member).filter(
            (Member.username == member_in.username) | (Member.email == member_in.email)
        ).first()
        if existing:
            return None

        hasher = PasswordHash.recommended()
        hashed_password = hasher.hash(member_in.password)

        db_member = Member(
            fullname=member_in.fullname,
            username=member_in.username,
            email=member_in.email,
            password=hashed_password,
            mental_health_history=member_in.mental_health_history,
            academic_performance=member_in.academic_performance,
            social_support=member_in.social_support,
            role=MemberRole.MAHASISWA,
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal membuat mahasiswa baru") from e
