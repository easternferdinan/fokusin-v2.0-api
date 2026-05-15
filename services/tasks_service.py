from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, UTC
from typing import List
import uuid

from core.exceptions import DatabaseOperationError
from models.task import Task
from schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskCompletionRequest

def get_tasks_service(db: Session) -> List[Task]:
    """
    Retrieve all tasks.
    """
    try:
        return db.query(Task).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve tasks") from e

def get_task_service(db: Session, task_id: str) -> Task | None:
    """
    Retrieve a specific task by ID.
    """
    try:
        return db.query(Task).filter(Task.task_id == uuid.UUID(task_id)).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError(f"Failed to retrieve task {task_id}") from e

def create_task_service(db: Session, task: TaskCreateRequest) -> Task:
    """
    Create a new task.
    """
    try:
        db_task = Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to create task") from e

def update_task_service(db: Session, task_id: str, task_in: TaskUpdateRequest) -> Task | None:
    """
    Update an existing task.
    """
    try:
        db_task = db.query(Task).filter(Task.task_id == uuid.UUID(task_id)).first()
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

def delete_task_service(db: Session, task_id: str) -> bool:
    """
    Delete a task.
    """
    try:
        db_task = db.query(Task).filter(Task.task_id == uuid.UUID(task_id)).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError(f"Failed to delete task {task_id}") from e

def complete_task_service(db: Session, task_id: str, completion_in: TaskCompletionRequest) -> Task | None:
    """
    Mark a task as complete or incomplete.
    """
    try:
        db_task = db.query(Task).filter(Task.task_id == uuid.UUID(task_id)).first()
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