from enums.report_enums import ReportRecommendationColorLabelEnum, ReportRecommendationSubjectEnum
from schemas.report import RecommendationResponse
import uuid
from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session

from core.exceptions import DatabaseOperationError
from models.stress_analysis import StressAnalysis
from schemas.report import StressTrendResponse, PotentialStressFactorsResponse
from enums.stress_level import StressLevelEnum
from utils.categorize import three_level_categorize
from services.tasks_service import get_incomplete_tasks_service, get_deadline_is_tomorrow_tasks_service
from services.stress_analysis_service import get_sleep_quality_service, get_all_stress_analysis_service

def get_stress_trend_service(db: Session, user_id: uuid.UUID, period: str) -> StressTrendResponse:
    '''
    Get stress trend for the current user.

    Args:
        db (Session): Database session
        user_id (uuid.UUID): User ID
        period (str): Period for stress trend ['harian', 'mingguan', 'bulanan']

    Returns:
        dict:
            - labels (list): Labels for stress trend (e.g. ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'])
            - values (list): Values for stress trend (e.g. [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    
    Raises:
        ValueError: If period is invalid
        DatabaseOperationError: If database operation fails
    '''
    try:
        today = datetime.now(UTC).date()
        
        if period == 'harian':
            start_date = today - timedelta(days=6)
        elif period == 'mingguan':
            start_date = today - timedelta(days=27)
        elif period == 'bulanan':
            start_date = (today.replace(day=1) - timedelta(days=150)).replace(day=1)
        else:
            raise ValueError("Invalid period")

        records = db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id,
            StressAnalysis.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=UTC)
        ).order_by(StressAnalysis.created_at.asc()).all()

        stress_value_map = {
            StressLevelEnum.RENDAH: 1,
            StressLevelEnum.SEDANG: 2,
            StressLevelEnum.TINGGI: 3,
        }

        DAY_LABELS_ID = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
        MONTH_LABELS_ID = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

        labels = []
        values = []

        if period == 'harian':
            buckets = {start_date + timedelta(days=day_offset): [] for day_offset in range(7)}
            for record in records:
                record_date = record.created_at.date()
                if record_date in buckets:
                    buckets[record_date].append(stress_value_map[record.stress_level])
            
            for bucket_date, stress_scores in buckets.items():
                labels.append(DAY_LABELS_ID[bucket_date.weekday()])
                values.append(sum(stress_scores) / len(stress_scores) if stress_scores else 0.0)
                
        elif period == 'mingguan':
            buckets = []
            for week_offset in range(4):
                week_start_date = today - timedelta(days=27 - week_offset * 7)
                week_end_date = week_start_date + timedelta(days=6)
                buckets.append({"start": week_start_date, "end": week_end_date, "stress_scores": []})
                
            for record in records:
                record_date = record.created_at.date()
                for week_bucket in buckets:
                    if week_bucket["start"] <= record_date <= week_bucket["end"]:
                        week_bucket["stress_scores"].append(stress_value_map[record.stress_level])
                        break
            
            for week_bucket in buckets:
                week_start_date = week_bucket['start']
                label = f"{week_start_date.day} {MONTH_LABELS_ID[week_start_date.month]}"
                labels.append(label)
                stress_scores = week_bucket["stress_scores"]
                values.append(sum(stress_scores) / len(stress_scores) if stress_scores else 0.0)

        elif period == 'bulanan':
            target_months = []
            for month_offset in range(5, -1, -1):
                target_month = today.month - month_offset
                target_year = today.year
                if target_month <= 0:
                    target_month += 12
                    target_year -= 1
                target_months.append((target_year, target_month))
                
            buckets = { (target_year, target_month): [] for target_year, target_month in target_months }
            for record in records:
                year_month_key = (record.created_at.year, record.created_at.month)
                if year_month_key in buckets:
                    buckets[year_month_key].append(stress_value_map[record.stress_level])
            
            for (target_year, target_month), stress_scores in buckets.items():
                labels.append(MONTH_LABELS_ID[target_month])
                values.append(sum(stress_scores) / len(stress_scores) if stress_scores else 0.0)

        return StressTrendResponse(labels=labels, values=values)
    except Exception as error:
        raise DatabaseOperationError(f"Failed to get stress trend: {str(error)}") from error

def get_potential_stress_factors_service(db: Session, user_id: uuid.UUID) -> PotentialStressFactorsResponse:
    deadline_is_tomorrow_tasks = get_deadline_is_tomorrow_tasks_service(db, user_id, count_only=True)
    piling_up_tasks = get_incomplete_tasks_service(db, user_id, count_only=True)
    sleep_quality_list = get_sleep_quality_service(db, user_id, past_days_count=3)

    sleep_quality_mode: int
    sleep_quality_counts = {
        1: 0,
        2: 0,
        3: 0,
    }

    for sleep_quality in sleep_quality_list:
        if sleep_quality in sleep_quality_counts:
            sleep_quality_counts[sleep_quality] += 1
        else:
            sleep_quality_counts[sleep_quality] = 1
    
    sleep_quality_mode = max(sleep_quality_counts, key=sleep_quality_counts.get)

    return PotentialStressFactorsResponse(
        deadline_is_tomorrow_tasks=three_level_categorize(deadline_is_tomorrow_tasks, 0, 2),
        piling_up_tasks=three_level_categorize(piling_up_tasks, 3, 6),
        sleep_quality=three_level_categorize(sleep_quality_mode, 1, 2, ["buruk", "sedang", "baik"])
    )

# TODO: Refactor this abomination if possible. I hate it.
# TODO: Add more "recommendations" based on other stress triggers. e.g. > 3 high priority tasks with < 3 days deadlines or > 5 medium priority tasks with < 3 days deadlines, etc.
def get_recommendations_service(db: Session, user_id: uuid.UUID, potential_stress_factors: PotentialStressFactorsResponse) -> list[RecommendationResponse]:
    recommendations: list[RecommendationResponse] = []

    deadline_is_tomorrow_tasks = potential_stress_factors.deadline_is_tomorrow_tasks
    piling_up_tasks = potential_stress_factors.piling_up_tasks
    sleep_quality = potential_stress_factors.sleep_quality

    if deadline_is_tomorrow_tasks == "tinggi":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.DEADLINE_IS_TOMORROW_TASKS.value,
            color_label=ReportRecommendationColorLabelEnum.DANGER.value,
            messages=[
                "Kamu memiliki banyak tugas dengan tenggat waktu penyelesaian besok.",
                "Prioritaskan mengerjakan tugas-tugas tersebut agar tidak terlambat."
            ]
        ))
    if piling_up_tasks == "tinggi":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.PILING_UP_TASKS.value,
            color_label=ReportRecommendationColorLabelEnum.DANGER.value,
            messages=[
                "Tugasmu yang belum selesai sudah menumpuk.",
                "Segera selesaikan tugas-tugas tersebut berdasarkan urgensi dan tingkat kepentingannya."
            ]
        ))
    if sleep_quality == "buruk":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.SLEEP_QUALITY.value,
            color_label=ReportRecommendationColorLabelEnum.DANGER.value,
            messages=[
                "Kualitas tidurmu kurang baik dalam 3 hari terakhir.",
                "Usahakan tidur 7-8 jam setiap malam untuk menjaga kesehatan mental dan fisik!"
            ]
        ))

    if deadline_is_tomorrow_tasks == "sedang":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.DEADLINE_IS_TOMORROW_TASKS.value,
            color_label=ReportRecommendationColorLabelEnum.WARNING.value,
            messages=[
                "Kamu memiliki beberapa tugas dengan tenggat waktu penyelesaian besok.",
                "Kerjakan tugas-tugas tersebut agar tidak terlambat."
            ]
        ))
    if piling_up_tasks == "sedang":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.PILING_UP_TASKS.value,
            color_label=ReportRecommendationColorLabelEnum.WARNING.value,
            messages=[
                "Kamu memiliki beberapa tugas yang mulai menumpuk.",
                "Segera selesaikan satu per satu agar waktu istirahatmu tetap terjaga."
            ]
        ))
    if sleep_quality == "sedang":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.SLEEP_QUALITY.value,
            color_label=ReportRecommendationColorLabelEnum.WARNING.value,
            messages=[
                "Kualitas tidurmu dalam 3 hari terakhir masih bisa ditingkatkan.",
                "Cobalah untuk tidak mengkonsumsi kafein dan menggunakan gadget terlalu dekat dengan waktu tidur!"
            ]
        ))

    if deadline_is_tomorrow_tasks == "rendah" and piling_up_tasks == "rendah" and sleep_quality == "baik":
        recommendations.append(RecommendationResponse(
            subject=ReportRecommendationSubjectEnum.OTHER.value,
            color_label=ReportRecommendationColorLabelEnum.SUCCESS.value,
            messages=[
                "Tugas dan kualitas tidurmu sudah terkelola dengan baik.",
                "Terus pertahankan untuk menjaga kesehatan mental dan fisik!"
            ]
        ))

    return recommendations

def get_stress_report_service(db: Session, user_id: uuid.UUID) -> dict:
    all_stress_analysis = get_all_stress_analysis_service(db, user_id)
    potential_stress_factors = get_potential_stress_factors_service(db, user_id)
    recommendations = get_recommendations_service(db, user_id, potential_stress_factors)
    
    return {
        "all_stress_analysis": all_stress_analysis,
        "potential_stress_factors": potential_stress_factors,
        "recommendations": recommendations
    }