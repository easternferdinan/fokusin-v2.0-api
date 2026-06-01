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
    