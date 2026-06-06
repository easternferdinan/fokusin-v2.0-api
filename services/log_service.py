from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import uuid

from core.exceptions import DatabaseOperationError
from models.log import Log
from models.member import Member
from schemas.log import LogCreateRequest
from enums.log_enums import LogLevel

def create_log_service(db: Session, log_in: LogCreateRequest) -> Log:
    """
    Create a new log entry in the database.
    """
    try:
        db_log = Log(**log_in.model_dump())
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create log entry") from e

def get_logs_service(
    db: Session, 
    user_id: Optional[uuid.UUID] = None, 
    level: Optional[LogLevel] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
) -> List[Log]:
    """
    Retrieve logs with optional filtering.
    """
    try:
        query = db.query(Log).options(joinedload(Log.member))
        
        if user_id:
            query = query.filter(Log.user_id == user_id)
        if level:
            query = query.filter(Log.level == level)
        if event_type:
            query = query.filter(Log.event_type == event_type)
            
        return query.order_by(Log.created_at.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve logs") from e

def get_user_logs_service(db: Session, user_id: uuid.UUID, limit: int = 50) -> List[Log]:
    """
    Retrieve logs for a specific user.
    """
    return get_logs_service(db, user_id=user_id, limit=limit)


def log_user_action(db: Session, user: Member, event_type: str, message: str, extra_data: dict | None = None) -> Log:
    """
    Convenience helper to create a log entry for an authenticated user action.
    """
    log_in = LogCreateRequest(
        user_id=user.user_id,
        level=LogLevel.INFO,
        event_type=event_type,
        message=message,
        extra_data=extra_data,
    )
    return create_log_service(db, log_in)
