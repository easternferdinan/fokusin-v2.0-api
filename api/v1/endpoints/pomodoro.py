from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, get_current_user
from models.member import Member
from schemas.pomodoro import PomodoroCreateRequest, PomodoroResponse, PomodoroUpdateRequest
from services.pomodoro_service import (
    get_pomodoros_service,
    get_pomodoro_service,
    create_pomodoro_service,
    update_pomodoro_service,
    resume_pomodoro_service,
    pause_pomodoro_service,
    complete_pomodoro_service,
    delete_pomodoro_service
)

router = APIRouter()

@router.get("/", response_model=List[PomodoroResponse])
def get_pomodoros(db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Retrieve all pomodoro sessions for the current user.
    """
    return get_pomodoros_service(db, current_user.user_id)

@router.post("/", response_model=PomodoroResponse, status_code=status.HTTP_201_CREATED)
def create_pomodoro(pomodoro_in: PomodoroCreateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Log a new pomodoro session for the current user.
    """
    return create_pomodoro_service(db, pomodoro_in, current_user.user_id)

@router.get("/{pomodoro_id}", response_model=PomodoroResponse)
def get_pomodoro(pomodoro_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Get a specific pomodoro session by ID for the current user.
    """
    pomodoro = get_pomodoro_service(db, pomodoro_id, current_user.user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return pomodoro

@router.put("/{pomodoro_id}", response_model=PomodoroResponse)
def update_pomodoro(pomodoro_id: str, pomodoro_in: PomodoroUpdateRequest, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Update an existing pomodoro session for the current user.
    """
    pomodoro = update_pomodoro_service(db, pomodoro_id, pomodoro_in, current_user.user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return pomodoro

@router.patch("/{pomodoro_id}/resume", response_model=PomodoroResponse)
def resume_pomodoro(pomodoro_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Resume a paused pomodoro session for the current user.
    """
    pomodoro = get_pomodoro_service(db, pomodoro_id, current_user.user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return resume_pomodoro_service(db, pomodoro_id, current_user.user_id)

@router.patch("/{pomodoro_id}/pause", response_model=PomodoroResponse)
def pause_pomodoro(pomodoro_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Pause an active pomodoro session for the current user.
    """
    pomodoro = get_pomodoro_service(db, pomodoro_id, current_user.user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return pause_pomodoro_service(db, pomodoro_id, current_user.user_id)

@router.patch("/{pomodoro_id}/complete", response_model=PomodoroResponse)
def complete_pomodoro(pomodoro_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Mark a pomodoro session as complete for the current user.
    """
    pomodoro = get_pomodoro_service(db, pomodoro_id, current_user.user_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return complete_pomodoro_service(db, pomodoro_id, current_user.user_id)

@router.delete("/{pomodoro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pomodoro(pomodoro_id: str, db: Session = Depends(get_db), current_user: Member = Depends(get_current_user)):
    """
    Delete a pomodoro session for the current user.
    """
    success = delete_pomodoro_service(db, pomodoro_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return None
