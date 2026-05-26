from models.member import Member
from api.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db
from schemas.member import UserCreateRequest, UserResponse, UserAuthenticationRequest, UserAuthenticationSuccessResponse, UserAuthenticationFailedResponse, UserUpdateRequest
from services.auth_service import (
    register_user_service,
    authenticate_user_service,
    update_user_service
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new member.
    """
    user = register_user_service(db, user_in)

    # If register_user_service return None, it means username or email already exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username atau email sudah terdaftar"
        )

    return user

@router.post("/login", response_model=UserAuthenticationSuccessResponse)
def login(auth_in: UserAuthenticationRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a token.
    """
    user = authenticate_user_service(db, auth_in)
    
    if not user.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    
    return user

@router.put("/update", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(user_in: UserUpdateRequest, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    updated_user = update_user_service(db, user.user_id, user_in)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    return user