from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
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
def get_tasks(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Retrieve all tasks for the current user.
    """
    return get_tasks_service(db, current_user.user_id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Get a specific task by ID for the current user.
    """
    task = get_task_service(db, task_id, current_user.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Create a new task for the current user.
    """
    return create_task_service(db, task_in, current_user.user_id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_in: TaskUpdateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Update an existing task for the current user.
    """
    task = update_task_service(db, task_id, task_in, current_user.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Delete a task for the current user.
    """
    success = delete_task_service(db, task_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, completion_in: TaskCompletionRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Mark a task as complete or incomplete for the current user.
    """
    task = complete_task_service(db, task_id, completion_in, current_user.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
