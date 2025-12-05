"""
Tests for authentication module.
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_password,
)
from app.config import settings


def test_verify_password():
    """Test password verification."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password = "testpassword"
    hashed = pwd_context.hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Decode token to verify contents
    payload = jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )
    
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_authenticate_user_success():
    """Test successful user authentication."""
    assert authenticate_user("demo", "demo123") is True


def test_authenticate_user_wrong_username():
    """Test authentication with wrong username."""
    assert authenticate_user("wronguser", "demo123") is False


def test_authenticate_user_wrong_password():
    """Test authentication with wrong password."""
    assert authenticate_user("demo", "wrongpassword") is False


def test_login_success(client: TestClient):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={"username": "demo", "password": "demo123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_credentials(client: TestClient):
    """Test login with wrong credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "wrong", "password": "wrong"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_protected_endpoint_without_token(client: TestClient):
    """Test accessing protected endpoint without token."""
    response = client.get("/v1/coins/")
    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client: TestClient):
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/v1/coins/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client: TestClient, auth_headers: dict):
    """Test accessing protected endpoint with valid token."""
    response = client.get("/v1/coins/", headers=auth_headers)
    # May get 200 or 503 depending on CoinGecko availability
    assert response.status_code in [200, 503, 504]
