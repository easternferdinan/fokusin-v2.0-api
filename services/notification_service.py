from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.notification import Notification
from schemas.notification import NotificationCreateRequest, NotificationUpdateRequest

def get_notifications_service(db: Session) -> List[Notification]:
    """
    Retrieve all notifications.
    """
    try:
        return db.query(Notification).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve notifications") from e

def get_notification_service(db: Session, notification_id: str) -> Notification | None:
    """
    Retrieve a specific notification by ID.
    """
    try:
        return db.query(Notification).filter(Notification.notification_id == uuid.UUID(notification_id)).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve notification {notification_id}") from e

def create_notification_service(db: Session, notification_in: NotificationCreateRequest) -> Notification:
    """
    Create a new notification.
    """
    try:
        db_notification = Notification(**notification_in.dict())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create notification") from e

def update_notification_service(db: Session, notification_id: str, notification_in: NotificationUpdateRequest) -> Notification | None:
    """
    Update an existing notification.
    """
    try:
        db_notification = db.query(Notification).filter(Notification.notification_id == uuid.UUID(notification_id)).first()
        if not db_notification:
            return None
        
        update_data = notification_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_notification, field, value)
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to update notification {notification_id}") from e

def delete_notification_service(db: Session, notification_id: str) -> bool:
    """
    Delete a notification.
    """
    try:
        db_notification = db.query(Notification).filter(Notification.notification_id == uuid.UUID(notification_id)).first()
        if not db_notification:
            return False
        
        db.delete(db_notification)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete notification {notification_id}") from e
