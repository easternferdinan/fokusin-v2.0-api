import jwt
from datetime import datetime, timedelta
from models.member import Member
from core.config import settings

def create_access_token(user:Member) -> str:
    """
    Create an access token for a user.
    """
    to_encode = {
        "user_id": str(user.user_id),
        "role": user.role,
        "exp": datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict:
    """
    Decode an access token.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])