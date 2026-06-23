from unittest.mock import MagicMock
from datetime import datetime, timedelta

import jwt
import pytest

from utils.jwt import create_access_token, decode_access_token
from core.config import settings


class TestCreateAccessToken:
    def test_create_token_contains_user_id_and_role(self, mock_user):
        token = create_access_token(mock_user)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["user_id"] == str(mock_user.user_id)
        assert payload["role"] == mock_user.role

    def test_token_has_expiry(self, mock_user):
        token = create_access_token(mock_user)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "exp" in payload
        assert isinstance(payload["exp"], int)


class TestDecodeAccessToken:
    def test_decode_valid_token_returns_payload(self, mock_user):
        token = create_access_token(mock_user)
        payload = decode_access_token(token)
        assert payload["user_id"] == str(mock_user.user_id)
        assert payload["role"] == mock_user.role

    def test_decode_expired_token_raises_error(self, mock_user):
        payload = {
            "user_id": str(mock_user.user_id),
            "role": "mahasiswa",
            "exp": int((datetime.now() - timedelta(hours=1)).timestamp())
        }
        expired_token = jwt.encode(
            payload, settings.secret_key, algorithm=settings.algorithm
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(expired_token)

    def test_decode_invalid_token_raises_error(self):
        with pytest.raises(jwt.PyJWTError):
            decode_access_token("invalid.token.here")
