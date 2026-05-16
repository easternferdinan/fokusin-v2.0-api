from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.pomodoro_session import PomodoroSession
from schemas.pomodoro import PomodoroCreateRequest, PomodoroUpdateRequest

def get_pomodoros_service(db: Session, user_id: uuid.UUID) -> List[PomodoroSession]:
    """
    Retrieve all pomodoro sessions for a specific user.
    """
    try:
        return db.query(PomodoroSession).filter(PomodoroSession.user_id == user_id).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve pomodoro sessions") from e

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
        db_pomodoro = PomodoroSession(**pomodoro_in.dict(), user_id=user_id)
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
