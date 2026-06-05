import uuid
from typing import List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, cast, Date
from pwdlib import PasswordHash
from datetime import datetime, timedelta, UTC
from collections import Counter

from core.exceptions import DatabaseOperationError
from enums.member_enums import MemberRole
from models.member import Member
from models.stress_analysis import StressAnalysis
from schemas.admin import (
    MahasiswaCreateByAdminRequest, 
    AdminDashboardResponse, 
    StressLevelPercentage, 
    CorrelatedAcademicStressStats, 
    CorrelatedSocialStressStats, 
    DailyStressTrend,
    DailyStressTrendResponse
)
from enums.stress_level import StressLevelEnum

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


def get_admin_dashboard_data_service(db: Session) -> AdminDashboardResponse:
    try:
        # Total mahasiswa
        total_mahasiswa = db.query(Member).filter(Member.role == MemberRole.MAHASISWA).count()

        if total_mahasiswa == 0:
            return AdminDashboardResponse(
                total_mahasiswa=0,
                stress_level_percentages=StressLevelPercentage(tinggi=0.0, sedang=0.0, rendah=0.0),
                correlated_academic_stress_stats=CorrelatedAcademicStressStats(academic_1_2_high_stress=0.0, academic_3_5_high_stress=0.0),
                correlated_social_stress_stats=CorrelatedSocialStressStats(social_0_high_stress=0.0, social_1_high_stress=0.0, social_2_high_stress=0.0, social_3_high_stress=0.0)
            )

        # Correlated subquery for latest stress level
        latest_stress_subq = (
            select(StressAnalysis.stress_level)
            .where(StressAnalysis.user_id == Member.user_id)
            .order_by(StressAnalysis.created_at.desc())
            .limit(1)
            .correlate(Member)
            .scalar_subquery()
        )

        results = db.query(
            Member.academic_performance,
            Member.mental_health_history,
            Member.social_support,
            latest_stress_subq.label('latest_stress_level')
        ).filter(
            Member.role == MemberRole.MAHASISWA
        ).all()

        tinggi_count = sum(1 for r in results if r.latest_stress_level == StressLevelEnum.TINGGI)
        sedang_count = sum(1 for r in results if r.latest_stress_level == StressLevelEnum.SEDANG)
        rendah_count = sum(1 for r in results if r.latest_stress_level == StressLevelEnum.RENDAH)
        total_with_stress = tinggi_count + sedang_count + rendah_count

        # Percentages
        if total_with_stress > 0:
            stress_level_percentages = StressLevelPercentage(
                tinggi=round(tinggi_count / total_with_stress * 100, 2),
                sedang=round(sedang_count / total_with_stress * 100, 2),
                rendah=round(rendah_count / total_with_stress * 100, 2)
            )
        else:
            stress_level_percentages = StressLevelPercentage(tinggi=0.0, sedang=0.0, rendah=0.0)

        # Correlated Academic
        acad_1_2_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.academic_performance in [1, 2]]
        acad_3_5_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.academic_performance in [3, 4, 5]]
        
        correlated_academic = CorrelatedAcademicStressStats(
            mode_academic_1_2=Counter(acad_1_2_levels).most_common(1)[0][0] if acad_1_2_levels else None,
            mode_academic_3_5=Counter(acad_3_5_levels).most_common(1)[0][0] if acad_3_5_levels else None
        )

        soc_1_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.social_support == 1]
        soc_2_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.social_support == 2]
        soc_3_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.social_support == 3]

        correlated_social = CorrelatedSocialStressStats(
            mode_social_1=Counter(soc_1_levels).most_common(1)[0][0] if soc_1_levels else None,
            mode_social_2=Counter(soc_2_levels).most_common(1)[0][0] if soc_2_levels else None,
            mode_social_3=Counter(soc_3_levels).most_common(1)[0][0] if soc_3_levels else None,
        )

        # # Correlated Social
        # soc_0_1_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.social_support in [0, 1]]
        # soc_2_3_levels = [r.latest_stress_level for r in results if r.latest_stress_level and r.social_support in [2, 3]]
        
        # correlated_social = CorrelatedSocialStressStats(
        #     mode_social_0_1=Counter(soc_0_1_levels).most_common(1)[0][0] if soc_0_1_levels else None,
        #     mode_social_2_3=Counter(soc_2_3_levels).most_common(1)[0][0] if soc_2_3_levels else None
        # )

        correlated_mental_health_history = [r.latest_stress_level for r in results if r.latest_stress_level and r.mental_health_history]
        not_correlated_mental_health_history = [r.latest_stress_level for r in results if r.latest_stress_level and not r.mental_health_history]

        correlated_mental_health_history_percentages = StressLevelPercentage(
            tinggi=round(correlated_mental_health_history.count(StressLevelEnum.TINGGI) / len(correlated_mental_health_history) * 100, 2),
            sedang=round(correlated_mental_health_history.count(StressLevelEnum.SEDANG) / len(correlated_mental_health_history) * 100, 2),
            rendah=round(correlated_mental_health_history.count(StressLevelEnum.RENDAH) / len(correlated_mental_health_history) * 100, 2)
        )
        not_correlated_mental_health_history_percentages = StressLevelPercentage(
            tinggi=round(not_correlated_mental_health_history.count(StressLevelEnum.TINGGI) / len(not_correlated_mental_health_history) * 100, 2),
            sedang=round(not_correlated_mental_health_history.count(StressLevelEnum.SEDANG) / len(not_correlated_mental_health_history) * 100, 2),
            rendah=round(not_correlated_mental_health_history.count(StressLevelEnum.RENDAH) / len(not_correlated_mental_health_history) * 100, 2)
        )

        mental_health_history_effect: str
        if correlated_mental_health_history_percentages.tinggi > not_correlated_mental_health_history_percentages.tinggi:
            mental_health_history_effect = "Sistem mendeteksi bahwa persentase mahasiswa dengan riwayat masalah kesehatan mental cenderung memiliki tingkat stres lebih tinggi dibandingkan yang tidak memiliki riwayat."
        elif correlated_mental_health_history_percentages.tinggi < not_correlated_mental_health_history_percentages.tinggi:
            mental_health_history_effect = "Sistem mendeteksi bahwa persentase mahasiswa dengan riwayat masalah kesehatan mental cenderung memiliki tingkat stres lebih rendah dibandingkan yang tidak memiliki riwayat."
        else:
            mental_health_history_effect = "Tidak ada korelasi yang signifikan antara riwayat masalah kesehatan mental dan tingkat stres mahasiswa."

        return AdminDashboardResponse(
            total_mahasiswa=total_mahasiswa,
            stress_level_percentages=stress_level_percentages,
            correlated_academic_stress_stats=correlated_academic,
            correlated_social_stress_stats=correlated_social,
            mental_health_history_effect=mental_health_history_effect
        )
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil data dashboard") from e


def get_admin_daily_stress_trend_service(db: Session, period: str) -> DailyStressTrendResponse:
    try:
        now = datetime.now(UTC)
        if period == "last_month":
            start_date = now - timedelta(days=60)
            end_date = now - timedelta(days=30)
        else: # "this_month"
            start_date = now - timedelta(days=30)
            end_date = now

        trend_results = db.query(
            cast(StressAnalysis.created_at, Date).label('date'),
            StressAnalysis.stress_level
        ).filter(
            StressAnalysis.created_at >= start_date,
            StressAnalysis.created_at <= end_date,
            StressAnalysis.user_id.in_(
                select(Member.user_id).where(Member.role == MemberRole.MAHASISWA)
            )
        ).all()

        trend_dict = {}
        for row in trend_results:
            d = row.date.strftime("%Y-%m-%d")
            if d not in trend_dict:
                trend_dict[d] = []
            trend_dict[d].append(row.stress_level)

        INDONESIAN_MONTHS = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
            7: "Jul", 8: "Agt", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
        }

        daily_stress_trend = []
        for i in range(30, -1, -1):
            day = (end_date - timedelta(days=i)).date()
            d_str = day.strftime("%Y-%m-%d")
            
            label_str = f"{day.day} {INDONESIAN_MONTHS[day.month]}"
            
            if d_str in trend_dict and trend_dict[d_str]:
                counter = Counter(trend_dict[d_str])
                mode_stress = counter.most_common(1)[0][0]
            else:
                mode_stress = None

            daily_stress_trend.append(DailyStressTrend(
                date=d_str,
                label=label_str,
                mode_stress=mode_stress
            ))

        return DailyStressTrendResponse(items=daily_stress_trend)

    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil data trend stress dashboard") from e
