"""
Pytest configuration and fixtures.

Provides common fixtures for testing the application.
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token
from app.main import app


@pytest.fixture
def client() -> Generator:
    """
    Create a test client for the FastAPI application.
    
    Yields:
        TestClient instance
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_token() -> str:
    """
    Create a valid JWT token for testing authenticated endpoints.
    
    Returns:
        JWT token string
    """
    return create_access_token(data={"sub": "demo"})


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """
    Create authorization headers with a valid token.
    
    Args:
        auth_token: JWT token from auth_token fixture
        
    Returns:
        Dictionary with authorization header
    """
    return {"Authorization": f"Bearer {auth_token}"}
