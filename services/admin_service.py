from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from typing import List

from core.exceptions import DatabaseOperationError
from enums.member_enums import MemberRole
from models.member import Member
from models.stress_analysis import StressAnalysis

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
