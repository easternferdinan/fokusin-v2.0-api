import pytest
from sqlalchemy.exc import SQLAlchemyError

from services.auth_service import register_user_service, authenticate_user_service
from schemas.member import UserCreateRequest, UserAuthenticationRequest
from core.exceptions import DatabaseOperationError


class TestRegisterUserService:
    def test_register_success(self, mock_db, mocker):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mocker.patch("services.auth_service.PasswordHash.recommended")
        user_in = UserCreateRequest(
            fullname="New User",
            username="newuser",
            email="new@example.com",
            password="password123",
            mental_health_history=False,
            academic_performance=3,
            social_support=2,
        )
        result = register_user_service(mock_db, user_in)
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_register_duplicate_username(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        user_in = UserCreateRequest(
            fullname="Duplicate User",
            username="testuser",
            email="new@example.com",
            password="password123",
            mental_health_history=False,
            academic_performance=3,
            social_support=2,
        )
        result = register_user_service(mock_db, user_in)
        assert result is None
        mock_db.add.assert_not_called()

    def test_register_duplicate_email(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        user_in = UserCreateRequest(
            fullname="Duplicate User",
            username="uniqueuser",
            email="test@example.com",
            password="password123",
            mental_health_history=False,
            academic_performance=3,
            social_support=2,
        )
        result = register_user_service(mock_db, user_in)
        assert result is None
        mock_db.add.assert_not_called()

    def test_register_database_error_raises(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError("DB error")
        user_in = UserCreateRequest(
            fullname="New User",
            username="newuser",
            email="new@example.com",
            password="password123",
            mental_health_history=False,
            academic_performance=3,
            social_support=2,
        )
        with pytest.raises(DatabaseOperationError):
            register_user_service(mock_db, user_in)


class TestAuthenticateUserService:
    def test_authenticate_success(self, mock_db, mock_user, mocker):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mocker.patch("services.auth_service.PasswordHash.recommended")
        mock_verify = mocker.patch("services.auth_service.PasswordHash.recommended")
        mock_verify.return_value.verify.return_value = True
        mocker.patch("services.auth_service.create_access_token", return_value="test-token-123")

        auth_in = UserAuthenticationRequest(username="testuser", password="password123")
        result = authenticate_user_service(mock_db, auth_in)

        assert result.authenticated is True
        assert result.access_token == "test-token-123"
        assert result.username == mock_user.username

    def test_authenticate_wrong_password(self, mock_db, mock_user, mocker):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mocker.patch("services.auth_service.PasswordHash.recommended")
        mock_verify = mocker.patch("services.auth_service.PasswordHash.recommended")
        mock_verify.return_value.verify.return_value = False

        auth_in = UserAuthenticationRequest(username="testuser", password="wrongpassword")
        result = authenticate_user_service(mock_db, auth_in)

        assert result.authenticated is False
        assert "Invalid username or password" in result.error

    def test_authenticate_user_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        auth_in = UserAuthenticationRequest(username="unknown", password="password123")
        result = authenticate_user_service(mock_db, auth_in)

        assert result.authenticated is False
        assert "Invalid username or password" in result.error

    def test_authenticate_database_error_raises(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.side_effect = SQLAlchemyError("DB error")
        auth_in = UserAuthenticationRequest(username="testuser", password="password123")
        with pytest.raises(DatabaseOperationError):
            authenticate_user_service(mock_db, auth_in)
