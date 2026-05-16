from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.notification import Notification
from schemas.notification import NotificationCreateRequest, NotificationUpdateRequest

def get_notifications_service(db: Session, user_id: uuid.UUID) -> List[Notification]:
    """
    Retrieve all notifications for a specific user.
    """
    try:
        return db.query(Notification).filter(Notification.user_id == user_id).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve notifications") from e

def get_notification_service(db: Session, notification_id: str, user_id: uuid.UUID) -> Notification | None:
    """
    Retrieve a specific notification by ID for a specific user.
    """
    try:
        return db.query(Notification).filter(
            Notification.notification_id == uuid.UUID(notification_id),
            Notification.user_id == user_id
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve notification {notification_id}") from e

def create_notification_service(db: Session, notification_in: NotificationCreateRequest, user_id: uuid.UUID) -> Notification:
    """
    Create a new notification for a specific user.
    """
    try:
        db_notification = Notification(**notification_in.dict(), user_id=user_id)
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create notification") from e

def update_notification_service(db: Session, notification_id: str, notification_in: NotificationUpdateRequest, user_id: uuid.UUID) -> Notification | None:
    """
    Update an existing notification for a specific user.
    """
    try:
        db_notification = db.query(Notification).filter(
            Notification.notification_id == uuid.UUID(notification_id),
            Notification.user_id == user_id
        ).first()
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

def delete_notification_service(db: Session, notification_id: str, user_id: uuid.UUID) -> bool:
    """
    Delete a notification for a specific user.
    """
    try:
        db_notification = db.query(Notification).filter(
            Notification.notification_id == uuid.UUID(notification_id),
            Notification.user_id == user_id
        ).first()
        if not db_notification:
            return False
        
        db.delete(db_notification)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete notification {notification_id}") from e
