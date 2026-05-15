from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db
from schemas.pomodoro import PomodoroCreateRequest, PomodoroResponse, PomodoroUpdateRequest
from services.pomodoro_service import (
    get_pomodoros_service,
    get_pomodoro_service,
    create_pomodoro_service,
    update_pomodoro_service,
    delete_pomodoro_service
)

router = APIRouter()

@router.get("/", response_model=List[PomodoroResponse])
def get_pomodoros(db: Session = Depends(get_db)):
    """
    Retrieve all pomodoro sessions.
    """
    return get_pomodoros_service(db)

@router.post("/", response_model=PomodoroResponse, status_code=status.HTTP_201_CREATED)
def create_pomodoro(pomodoro_in: PomodoroCreateRequest, db: Session = Depends(get_db)):
    """
    Log a new pomodoro session.
    """
    return create_pomodoro_service(db, pomodoro_in)

@router.get("/{pomodoro_id}", response_model=PomodoroResponse)
def get_pomodoro(pomodoro_id: str, db: Session = Depends(get_db)):
    """
    Get a specific pomodoro session by ID.
    """
    pomodoro = get_pomodoro_service(db, pomodoro_id)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return pomodoro

@router.put("/{pomodoro_id}", response_model=PomodoroResponse)
def update_pomodoro(pomodoro_id: str, pomodoro_in: PomodoroUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing pomodoro session.
    """
    pomodoro = update_pomodoro_service(db, pomodoro_id, pomodoro_in)
    if not pomodoro:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return pomodoro

@router.delete("/{pomodoro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pomodoro(pomodoro_id: str, db: Session = Depends(get_db)):
    """
    Delete a pomodoro session.
    """
    success = delete_pomodoro_service(db, pomodoro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    return None
