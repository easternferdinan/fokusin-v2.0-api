from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from enums.log_enums import LogEvent
from schemas.notification import NotificationCreateRequest, NotificationResponse, NotificationUpdateRequest
from services.log_service import log_user_action
from services.notification_service import (
    get_notifications_service,
    get_notification_service,
    create_notification_service,
    update_notification_service,
    delete_notification_service
)

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Retrieve all notifications for the current user.
    """
    return get_notifications_service(db, current_user.user_id)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification_in: NotificationCreateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Create a new notification for the current user.
    """
    notification = create_notification_service(db, notification_in, current_user.user_id)
    log_user_action(db, current_user, LogEvent.CREATE, "Mahasiswa created notification")
    return notification

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Get a specific notification by ID for the current user.
    """
    notification = get_notification_service(db, notification_id, current_user.user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: str, notification_in: NotificationUpdateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Update an existing notification for the current user.
    """
    notification = update_notification_service(db, notification_id, notification_in, current_user.user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    log_user_action(db, current_user, LogEvent.UPDATE, f"Mahasiswa updated notification {notification_id}")
    return notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Delete a notification for the current user.
    """
    success = delete_notification_service(db, notification_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    log_user_action(db, current_user, LogEvent.DELETE, f"Mahasiswa deleted notification {notification_id}")
    return None
