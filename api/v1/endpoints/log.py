from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from api.deps import get_db, get_current_user
from models.member import Member
from enums.member_enums import MemberRole
from enums.log_enums import LogLevel
from schemas.log import LogCreateRequest, LogResponse
from services.log_service import (
    create_log_service,
    get_logs_service,
    get_user_logs_service
)

router = APIRouter()

@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(
    log_in: LogCreateRequest, 
    db: Session = Depends(get_db), 
    current_user: Member = Depends(get_current_user)
):
    """
    Create a new log entry. If user_id is not provided in the request, 
    it will be automatically set to the current user's ID.
    """
    if not log_in.user_id:
        log_in.user_id = current_user.user_id
        
    return create_log_service(db, log_in)

@router.get("/", response_model=List[LogResponse])
def get_logs(
    level: Optional[LogLevel] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve logs. Non-admin users can only see their own logs.
    Admins can see all logs.
    """
    if current_user.role == MemberRole.SUPERADMIN:
        return get_logs_service(db, level=level, event_type=event_type, limit=limit, skip=skip)
    else:
        return get_user_logs_service(db, user_id=current_user.user_id, limit=limit)

@router.get("/me", response_model=List[LogResponse])
def get_my_logs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_user)
):
    """
    Retrieve logs for the current authenticated user.
    """
    return get_user_logs_service(db, user_id=current_user.user_id, limit=limit)
