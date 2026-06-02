from sqlalchemy import Date, func
from services.pomodoro_service import get_today_pomodoro_minutes_service
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, UTC
import uuid
from typing import List

from core.exceptions import DatabaseOperationError
from models.member import Member
from models.pomodoro_session import PomodoroSession
from models.stress_analysis import StressAnalysis
from schemas.stress_analysis import StressAnalysisCreateRequest, StressAnalysisRequirementsStatusResponse
from services.tasks_service import get_tasks_done_today_service
from ml.stress_predictor import get_predictor
from enums.stress_level import StressLevelEnum
from enums.task_enums import TaskPriority

def get_latest_stress_analysis_service(db: Session, user_id: uuid.UUID) -> StressAnalysis | None:
    """
    Retrieve the latest stress analysis for a specific user.
    """
    try:
        return db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id
        ).order_by(StressAnalysis.created_at.desc()).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve latest stress analysis") from e

def get_all_stress_analysis_service(db: Session, user_id: uuid.UUID) -> List[StressAnalysis]:
    """
    Retrieve all stress analysis for a specific user.
    """
    try:
        return db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id
        ).order_by(StressAnalysis.created_at.desc()).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve stress analysis") from e

def get_today_stress_assesment_count_service(db: Session, user_id: uuid.UUID) -> int:
    try:
        return db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id,
            StressAnalysis.created_at.cast(Date) == datetime.now(UTC).date()
        ).count()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve stress analysis count") from e

def calculate_study_load_service(db: Session, user_id: uuid.UUID) -> int:
    tasks_done_today = get_tasks_done_today_service(db, user_id)

    if not tasks_done_today:
        return 1

    priority_weights = {
        TaskPriority.RENDAH: 1.0,
        TaskPriority.SEDANG: 1.3,
        TaskPriority.TINGGI: 1.6,
    }

    today = datetime.now(UTC).date()
    total_weighted_minutes = 0.0

    for task in tasks_done_today:
        priority_weight = priority_weights.get(task.priority, 1.0)

        days_until_deadline = (task.deadline.date() - today).days
        if days_until_deadline > 3:
            deadline_weight = 1.0
        elif days_until_deadline >= 2:
            deadline_weight = 1.2
        elif days_until_deadline == 1:
            deadline_weight = 1.5
        else:
            deadline_weight = 1.8

        weighted_minutes = task.target_duration * priority_weight * deadline_weight
        total_weighted_minutes += weighted_minutes

    avg_elapsed_result = db.query(func.avg(PomodoroSession.elapsed_time)).filter(
        PomodoroSession.user_id == user_id,
        PomodoroSession.created_at.cast(Date) == today
    ).scalar()

    if not avg_elapsed_result:
        return 1

    avg_pomodoro_minutes = float(avg_elapsed_result)
    pomodoro_equivalent = total_weighted_minutes / avg_pomodoro_minutes

    if pomodoro_equivalent <= 1.5:
        return 1
    elif pomodoro_equivalent <= 3.5:
        return 2
    elif pomodoro_equivalent <= 5.5:
        return 3
    elif pomodoro_equivalent <= 8.5:
        return 4
    else:
        return 5

def create_stress_analysis_service(db: Session, data: StressAnalysisCreateRequest, user: Member) -> StressAnalysis:
    """
    Perform stress analysis and save the result.
    """
    try:
        # Inject mental_health_history, academic_performance, social_support from member
        # Inject study_load calculation
        ml_data = data.model_dump()
        ml_data["mental_health_history"] = user.mental_health_history
        ml_data["academic_performance"] = user.academic_performance
        ml_data["social_support"] = user.social_support
        ml_data["study_load"] = calculate_study_load_service(db, user.user_id)

        # Get the predictor and perform prediction
        predictor = get_predictor()
        prediction_result = predictor.predict(ml_data)
        
        # Map prediction result to Enum
        stress_mapping = {
            1: StressLevelEnum.RENDAH,
            2: StressLevelEnum.SEDANG,
            3: StressLevelEnum.TINGGI
        }
        
        stress_level = stress_mapping.get(int(prediction_result), StressLevelEnum.SEDANG)
        
        db_data = data.model_dump()
        db_data["study_load"] = ml_data["study_load"]
        
        # Create database record
        db_analysis = StressAnalysis(
            **db_data,
            user_id=user.user_id,
            stress_level=stress_level
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to save stress analysis") from e
    except Exception as e:
        db.rollback()
        # Log the error if needed
        raise DatabaseOperationError(f"An unexpected error occurred during stress analysis: {str(e)}") from e

def check_stress_analysis_requirements_service(db: Session, user_id: uuid.UUID) -> StressAnalysisRequirementsStatusResponse:
    try:
        task_done_today = len(get_tasks_done_today_service(db, user_id))
        pomodoro_done_today = get_today_pomodoro_minutes_service(db, user_id)
        stress_assesment_today = get_today_stress_assesment_count_service(db, user_id)

        response = StressAnalysisRequirementsStatusResponse()

        if task_done_today > 0:
            response.task_done_today = True
        
        if pomodoro_done_today > 0:
            response.pomodoro_done_today = True
        
        if stress_assesment_today > 0:
            response.stress_assesment_done_today = True
        
        return response
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to check report requirements") from e
    except Exception as e:
        raise DatabaseOperationError(f"An unexpected error occurred during check report requirements: {str(e)}") from e

def get_stress_trend_service(db: Session, user_id: uuid.UUID, period: str) -> dict:
    from datetime import timedelta
    import calendar
    
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

        labels = []
        values = []

        if period == 'harian':
            buckets = {start_date + timedelta(days=day_offset): [] for day_offset in range(7)}
            for record in records:
                record_date = record.created_at.date()
                if record_date in buckets:
                    buckets[record_date].append(stress_value_map[record.stress_level])
            
            for bucket_date, stress_scores in buckets.items():
                labels.append(bucket_date.strftime("%a"))
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
                label = f"{week_start_date.day} {week_start_date.strftime('%b')}"
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
                labels.append(calendar.month_abbr[target_month])
                values.append(sum(stress_scores) / len(stress_scores) if stress_scores else 0.0)

        return {"labels": labels, "values": values}
    except Exception as error:
        raise DatabaseOperationError(f"Failed to get stress trend: {str(error)}") from error

    