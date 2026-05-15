from sqlalchemy.orm import Session
from models.member import Member
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from fastapi import Depends, HTTPException, status
from typing import Generator, Any
from db.session import SessionLocal
from utils.jwt import decode_access_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_db() -> Generator:
    """
    Dependency to provide a database session to API endpoints.
    Ensures the session is closed after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict[Any, Any]:
    """
    Dependency to get the token payload.
    """
    try:
        payload = decode_access_token(token)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Member:
    """
    Dependency to get the current user.
    """
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(Member).filter(Member.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
