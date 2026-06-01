from sqlalchemy.orm import Session
from pydantic import UUID4

from services.stress_analysis_service import get_latest_stress_analysis_service
from services.tasks_service import get_deadline_is_tomorrow_tasks_service, get_high_priority_tasks_service, get_incomplete_tasks_service
from services.pomodoro_service import get_today_pomodoro_minutes_service

from schemas.dashboard import DashboardResponse

def get_dashboard_data_service(db: Session, user_id: UUID4) -> DashboardResponse:
    """
    Retrieve all data for the dashboard for the current user.
    """
    latest_stress_analysis = get_latest_stress_analysis_service(db, user_id)
    latest_burnout_prediction = latest_stress_analysis.stress_level.lower() if latest_stress_analysis else None

    incomplete_tasks_count = get_incomplete_tasks_service(db, user_id, count_only=True)
    high_priority_tasks_count = get_high_priority_tasks_service(db, user_id, count_only=True)
    deadline_is_tomorrow_tasks_count = get_deadline_is_tomorrow_tasks_service(db, user_id, count_only=True)
    today_pomodoro_minutes = get_today_pomodoro_minutes_service(db, user_id)
    deadline_is_tomorrow_tasks = get_deadline_is_tomorrow_tasks_service(db, user_id)

    return DashboardResponse(
        latest_burnout_prediction=latest_burnout_prediction,
        incomplete_tasks_count=incomplete_tasks_count,
        high_priority_tasks_count=high_priority_tasks_count,
        deadline_is_tomorrow_tasks_count=deadline_is_tomorrow_tasks_count,
        today_pomodoro_minutes=today_pomodoro_minutes,
        deadline_is_tomorrow_tasks=deadline_is_tomorrow_tasks
    )