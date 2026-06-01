from sqlalchemy import Date
from enums.task_enums import TaskPriority
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, UTC, timedelta
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.task import Task
from schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskCompletionRequest

def get_tasks_service(db: Session, user_id: uuid.UUID) -> List[Task]:
    """
    Retrieve all tasks for a specific user.
    """
    try:
        return db.query(Task).filter(Task.user_id == user_id).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve tasks") from e

def get_tasks_done_today_service(db: Session, user_id: uuid.UUID) -> List[Task]:
    """
    Retrieve all tasks for a specific user that are done today.
    """
    try:
        return db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == True,
            Task.completed_at.cast(Date) == datetime.now(UTC).date()
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve tasks done today") from e

def get_incomplete_tasks_service(db: Session, user_id: uuid.UUID, count_only: bool = False) -> List[Task] | int:
    """
    Retrieve or count all incomplete tasks for a specific user.
    """
    try:
        if count_only:
            return db.query(Task).filter(
                Task.user_id == user_id,
                Task.completed == False
            ).count()

        return db.query(Task).filter(
            Task.user_id == user_id,
            Task.completed == False
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve incomplete tasks") from e

def get_high_priority_tasks_service(db: Session, user_id: uuid.UUID, count_only: bool = False) -> List[Task] | int:
    """
    Retrieve or count all high priority tasks for a specific user.
    """
    try:
        if count_only:
            return db.query(Task).filter(
                Task.user_id == user_id,
                Task.priority == TaskPriority.TINGGI
            ).count()

        return db.query(Task).filter(
            Task.user_id == user_id,
            Task.priority == TaskPriority.TINGGI
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve high priority tasks") from e

def get_deadline_is_tomorrow_tasks_service(db: Session, user_id: uuid.UUID, count_only: bool = False) -> List[Task] | int:
    """
    Retrieve or count all tasks for a specific user that have a deadline of tomorrow.
    """
    try:
        if count_only:
            return db.query(Task).filter(
                Task.user_id == user_id,
                Task.deadline == datetime.now(UTC).date() + timedelta(days=1)
            ).count()

        return db.query(Task).filter(
            Task.user_id == user_id,
            Task.deadline == datetime.now(UTC).date() + timedelta(days=1)
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve deadline is tomorrow tasks") from e

def get_task_service(db: Session, task_id: str, user_id: uuid.UUID) -> Task | None:
    """
    Retrieve a specific task by ID for a specific user.
    """
    try:
        return db.query(Task).filter(
            Task.task_id == uuid.UUID(task_id),
            Task.user_id == user_id
        ).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve task {task_id}") from e

def create_task_service(db: Session, task: TaskCreateRequest, user_id: uuid.UUID) -> Task:
    """
    Create a new task for a specific user.
    """
    try:
        db_task = Task(**task.dict(), user_id=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create task") from e

def update_task_service(db: Session, task_id: str, task_in: TaskUpdateRequest, user_id: uuid.UUID) -> Task | None:
    """
    Update an existing task for a specific user.
    """
    try:
        db_task = db.query(Task).filter(
            Task.task_id == uuid.UUID(task_id),
            Task.user_id == user_id
        ).first()
        if not db_task:
            return None
        
        update_data = task_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to update task {task_id}") from e

def delete_task_service(db: Session, task_id: str, user_id: uuid.UUID) -> bool:
    """
    Delete a task for a specific user.
    """
    try:
        db_task = db.query(Task).filter(
            Task.task_id == uuid.UUID(task_id),
            Task.user_id == user_id
        ).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete task {task_id}") from e

def complete_task_service(db: Session, task_id: str, completion_in: TaskCompletionRequest, user_id: uuid.UUID) -> Task | None:
    """
    Mark a task as complete or incomplete for a specific user.
    """
    try:
        db_task = db.query(Task).filter(
            Task.task_id == uuid.UUID(task_id),
            Task.user_id == user_id
        ).first()
        if not db_task:
            return None
        
        db_task.completed = completion_in.completed
        if completion_in.completed:
            db_task.completed_at = datetime.now(UTC)
        else:
            db_task.completed_at = None
            
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to complete task {task_id}") from e