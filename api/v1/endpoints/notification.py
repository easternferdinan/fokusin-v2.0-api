from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db
from schemas.notification import NotificationCreateRequest, NotificationResponse, NotificationUpdateRequest
from services.notification_service import (
    get_notifications_service,
    get_notification_service,
    create_notification_service,
    update_notification_service,
    delete_notification_service
)

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    """
    Retrieve all notifications.
    """
    return get_notifications_service(db)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification_in: NotificationCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new notification.
    """
    return create_notification_service(db, notification_in)

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str, db: Session = Depends(get_db)):
    """
    Get a specific notification by ID.
    """
    notification = get_notification_service(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: str, notification_in: NotificationUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing notification.
    """
    notification = update_notification_service(db, notification_id, notification_in)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: str, db: Session = Depends(get_db)):
    """
    Delete a notification.
    """
    success = delete_notification_service(db, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return None
