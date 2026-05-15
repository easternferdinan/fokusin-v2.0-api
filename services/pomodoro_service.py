from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.pomodoro_session import PomodoroSession
from schemas.pomodoro import PomodoroCreateRequest, PomodoroUpdateRequest

def get_pomodoros_service(db: Session) -> List[PomodoroSession]:
    """
    Retrieve all pomodoro sessions.
    """
    try:
        return db.query(PomodoroSession).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve pomodoro sessions") from e

def get_pomodoro_service(db: Session, pomodoro_id: str) -> PomodoroSession | None:
    """
    Retrieve a specific pomodoro session by ID.
    """
    try:
        return db.query(PomodoroSession).filter(PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id)).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve pomodoro session {pomodoro_id}") from e

def create_pomodoro_service(db: Session, pomodoro_in: PomodoroCreateRequest) -> PomodoroSession:
    """
    Log a new pomodoro session.
    """
    try:
        db_pomodoro = PomodoroSession(**pomodoro_in.dict())
        db.add(db_pomodoro)
        db.commit()
        db.refresh(db_pomodoro)
        return db_pomodoro
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create pomodoro session") from e

def update_pomodoro_service(db: Session, pomodoro_id: str, pomodoro_in: PomodoroUpdateRequest) -> PomodoroSession | None:
    """
    Update an existing pomodoro session.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id)).first()
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

def delete_pomodoro_service(db: Session, pomodoro_id: str) -> bool:
    """
    Delete a pomodoro session.
    """
    try:
        db_pomodoro = db.query(PomodoroSession).filter(PomodoroSession.pomodoro_id == uuid.UUID(pomodoro_id)).first()
        if not db_pomodoro:
            return False
        
        db.delete(db_pomodoro)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete pomodoro session {pomodoro_id}") from e
