from models.member import Member
from api.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db
from core.exceptions import DatabaseOperationError
from enums.log_enums import LogEvent
from schemas.member import UserCreateRequest, UserResponse, UserAuthenticationRequest, UserAuthenticationSuccessResponse, UserAuthenticationFailedResponse, UserUpdateRequest, ChangePasswordRequest, ForgotPasswordRequest
from services.auth_service import (
    register_user_service,
    authenticate_user_service,
    update_user_service,
    change_password_service,
    forgot_password_service
)
from services.log_service import log_user_action

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

    log_user_action(db, user, LogEvent.CREATE, f"User registered: {user.username}")
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
    
    log_user_action(db, user, LogEvent.UPDATE, f"User updated profile: {user.username}")
    return user


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(pw_in: ChangePasswordRequest, db: Session = Depends(get_db), user: Member = Depends(get_current_user)):
    """
    Change password for the authenticated user. Verifies old password before updating.
    """
    try:
        change_password_service(db, user.user_id, pw_in)
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    log_user_action(db, user, LogEvent.UPDATE, f"User changed password: {user.username}")
    return {"message": "Password berhasil diubah"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(pw_in: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset a mahasiswa's password to their email.
    """
    try:
        forgot_password_service(db, pw_in)
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {"message": "Password berhasil direset ke email yang terdaftar"}