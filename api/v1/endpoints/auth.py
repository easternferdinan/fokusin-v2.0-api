from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db
from schemas.member import UserCreateRequest, UserResponse, UserAuthenticationRequest, UserAuthenticationResponse
from services.auth_service import (
    register_user_service,
    authenticate_user_service,
    get_user_by_username_or_email_service
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new member.
    """
    # Check if user already exists
    existing_user = get_user_by_username_or_email_service(db, user_in.username, user_in.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new member
    return register_user_service(db, user_in)

@router.post("/login", response_model=UserAuthenticationResponse)
def login(auth_in: UserAuthenticationRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a token.
    """
    user = authenticate_user_service(db, auth_in)
    
    if not user:
        return UserAuthenticationResponse(
            authenticated=False,
            error=["Invalid username or password"]
        )
    
    # TODO: Generate real JWT token
    mock_token = f"mock-jwt-token-for-{user.username}"
    
    return UserAuthenticationResponse(
        authenticated=True,
        access_token=mock_token
    )
