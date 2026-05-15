from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db
from schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest, TaskCompletionRequest
from services.tasks_service import (
    get_tasks_service,
    get_task_service,
    create_task_service,
    update_task_service,
    delete_task_service,
    complete_task_service
)

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks.
    """
    return get_tasks_service(db)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new task.
    """
    return create_task_service(db, task_in)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get a specific task by ID.
    """
    task = get_task_service(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_in: TaskUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing task.
    """
    task = update_task_service(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    success = delete_task_service(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, completion_in: TaskCompletionRequest, db: Session = Depends(get_db)):
    """
    Mark a task as complete or incomplete.
    """
    task = complete_task_service(db, task_id, completion_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
