from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pwdlib import PasswordHash

from core.exceptions import DatabaseOperationError
from models.member import Member
from schemas.member import UserCreateRequest, UserAuthenticationRequest, UserUpdateRequest, UserAuthenticationSuccessResponse, UserAuthenticationFailedResponse, ChangePasswordRequest, ForgotPasswordRequest
from enums.member_enums import MemberRole
from utils.jwt import create_access_token

def register_user_service(db: Session, user_in: UserCreateRequest) -> Member:
    """
    Register a new member.
    """
    try:
        existing_user = db.query(Member).filter(
            (Member.username == user_in.username) | (Member.email == user_in.email)
        ).first()

        if existing_user:
            return None

        hasher = PasswordHash.recommended()
        hashed_password = hasher.hash(user_in.password)

        # Create new member
        db_user = Member(
            fullname=user_in.fullname,
            username=user_in.username,
            email=user_in.email,
            password=hashed_password,
            mental_health_history=user_in.mental_health_history,
            academic_performance=user_in.academic_performance,
            social_support=user_in.social_support,
            role=MemberRole.MAHASISWA
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to register user") from e

def authenticate_user_service(db: Session, auth_in: UserAuthenticationRequest) -> UserAuthenticationSuccessResponse | UserAuthenticationFailedResponse:
    """
    Authenticate a user.
    """
    try:
        user = db.query(Member).filter(Member.username == auth_in.username).first()
        
        hasher = PasswordHash.recommended()
        if not user or not hasher.verify(auth_in.password, user.password):
            return UserAuthenticationFailedResponse(
                authenticated=False,
                error=["Invalid username or password"]
            )
        
        access_token = create_access_token(user)
        must_change_password = (auth_in.password == user.email)
        return UserAuthenticationSuccessResponse(
            fullname=user.fullname,
            username=user.username,
            email=user.email,
            mental_health_history=user.mental_health_history,
            academic_performance=user.academic_performance,
            social_support=user.social_support,
            role=user.role,
            authenticated=True,
            access_token=access_token,
            must_change_password=must_change_password
        )
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to authenticate user") from e

# def get_user_by_username_or_email_service(db: Session, username: str, email: str) -> Member | None:
#     """
#     Check if a user exists by username or email.
#     """
#     try:
#         return db.query(Member).filter(
#             (Member.username == username) | (Member.email == email)
#         ).first()
#     except SQLAlchemyError as e:
#         raise DatabaseOperationError("Failed to check user existence") from e

def update_user_service(db: Session, user_id: UUID4, user_in: UserUpdateRequest) -> Member:
    """
    Update an existing member.
    """
    try:
        user = db.query(Member).filter(Member.user_id == user_id).first()
        
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
        for field, value in update_data.items():
            setattr(user, field, value)

        if user_in.password is not None:
            hasher = PasswordHash.recommended()
            user.password = hasher.hash(user_in.password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to update user") from e


def change_password_service(db: Session, user_id: UUID4, pw_in: ChangePasswordRequest) -> Member:
    """
    Change password for an existing member, verifying old password first.
    """
    try:
        user = db.query(Member).filter(Member.user_id == user_id).first()

        if not user:
            raise DatabaseOperationError("User tidak ditemukan")

        hasher = PasswordHash.recommended()
        if not hasher.verify(pw_in.old_password, user.password):
            raise DatabaseOperationError("Password lama salah")

        user.password = hasher.hash(pw_in.new_password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal mengubah password") from e


def forgot_password_service(db: Session, pw_in: ForgotPasswordRequest) -> Member:
    """
    Reset a mahasiswa's password to their email.
    """
    try:
        user = db.query(Member).filter(Member.username == pw_in.username).first()

        if not user:
            raise DatabaseOperationError("Username tidak ditemukan")

        if user.role != MemberRole.MAHASISWA:
            raise DatabaseOperationError("Fitur ini hanya untuk mahasiswa")

        hasher = PasswordHash.recommended()
        user.password = hasher.hash(user.email)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal mereset password") from e
