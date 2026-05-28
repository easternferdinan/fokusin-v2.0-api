from datetime import UTC
from datetime import datetime
from sqlalchemy import Date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.pomodoro_session import PomodoroSession
from schemas.pomodoro import PomodoroCreateRequest, PomodoroUpdateRequest
from enums.pomodoro_enums import PomodoroStatus

def get_pomodoros_service(db: Session, user_id: uuid.UUID) -> List[PomodoroSession]:
    """
    Retrieve all pomodoro sessions for a specific user.
    """
    try:
        return db.query(PomodoroSession).filter(PomodoroSession.user_id == user_id).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve pomodoro sessions") from e

def get_today_pomodoros_service(db: Session, user_id: uuid.UUID) -> List[PomodoroSession]:
    """
    Retrieve all pomodoro sessions for a specific user that were created today.
    """
    try:
        return db.query(PomodoroSession).filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.created_at.cast(Date) == datetime.now().date()
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve pomodoro sessions") from e

def get_today_pomodoro_minutes_service(db: Session, user_id: uuid.UUID) -> int:
    """
    Retrieve the total pomodoro minutes for a specific user that were created today.
    """
    try:
        result = db.query(PomodoroSession.elapsed_time).filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.created_at.cast(Date) == datetime.now().date()
        ).all()

        total_minutes = sum(int(elapsed_time) for (elapsed_time,) in result if elapsed_time is not None)
        return int(total_minutes)
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve pomodoro minutes") from e

def get_pomodoro_service(db: Session, pomodoro_id: str, user_id: uuid.UUID) -> PomodoroSession | None:
    """
    Retrieve a specific pomodoro session by ID for a specific user.
    """
    try:
        return db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve pomodoro session {pomodoro_id}") from e

def create_pomodoro_service(db: Session, pomodoro_in: PomodoroCreateRequest, user_id: uuid.UUID) -> PomodoroSession:
    """
    Log a new pomodoro session for a specific user.
    """
    try:
        pomodoroData = {
            **pomodoro_in.dict(),
            "user_id": user_id,
            "session_start": datetime.now(UTC)
        }

        db_pomodoro = PomodoroSession(**pomodoroData)
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create pomodoro session") from e

def update_pomodoro_service(db: Session, pomodoro_id: str, pomodoro_in: PomodoroUpdateRequest, user_id: uuid.UUID) -> PomodoroSession | None:
    """
    Update an existing pomodoro session for a specific user.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
        if not db_pomodoro:
            return None
        
        update_data = pomodoro_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_pomodoro, field, value)
        
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to update pomodoro session {pomodoro_id}") from e

def resume_pomodoro_service(db: Session, pomodoro_id: str, user_id: uuid.UUID) -> PomodoroSession | None:
    """
    Resume a paused pomodoro session for a specific user.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
        if not db_pomodoro:
            return None
        
        if db_pomodoro.status != PomodoroStatus.PAUSED:
            raise DatabaseOperationError("Pomodoro session is not paused")
        
        db_pomodoro.status = PomodoroStatus.ACTIVE
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to resume pomodoro session {pomodoro_id}") from e

def pause_pomodoro_service(db: Session, pomodoro_id: str, user_id: uuid.UUID) -> PomodoroSession | None:
    """
    Pause an active pomodoro session for a specific user.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
        if not db_pomodoro:
            return None
        
        if db_pomodoro.status != PomodoroStatus.ACTIVE:
            raise DatabaseOperationError("Pomodoro session is not active")
        
        db_pomodoro.status = PomodoroStatus.PAUSED
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to pause pomodoro session {pomodoro_id}") from e

def complete_pomodoro_service(db: Session, pomodoro_id: str, user_id: uuid.UUID) -> PomodoroSession | None:
    """
    Mark a pomodoro session as complete for a specific user.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
        if not db_pomodoro:
            return None
        
        if db_pomodoro.status == PomodoroStatus.STOPPED:
            raise DatabaseOperationError("Pomodoro session is already stopped")
        
        db_pomodoro.status = PomodoroStatus.STOPPED
        db_pomodoro.completed = True
        
        now_utc = datetime.now(UTC)
        session_start_utc = db_pomodoro.session_start.replace(tzinfo=UTC) if db_pomodoro.session_start.tzinfo is None else db_pomodoro.session_start
        
        db_pomodoro.elapsed_time = int((now_utc - session_start_utc).total_seconds()) // 60
        db_pomodoro.session_end = now_utc
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to complete pomodoro session {pomodoro_id}") from e

def delete_pomodoro_service(db: Session, pomodoro_id: str, user_id: uuid.UUID) -> bool:
    """
    Delete a pomodoro session for a specific user.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(
            PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id),
            PomodoroSession.user_id == user_id
        ).first()
        if not db_pomodoro:
            return False
        
        db.delete(db_pomodoro)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete pomodoro session {pomodoro_id}") from e
