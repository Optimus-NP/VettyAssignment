"""
JWT-based authentication module.

Handles token generation, validation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_demo_user() -> dict:
    """
    Get demo user credentials from configuration.
    
    In production, replace this with database lookup.
    
    Returns:
        Dictionary with username and password hash
    """
    return {
        "username": settings.demo_username,
        "password_hash": pwd_context.hash(settings.demo_password),
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    
    return encoded_jwt


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password.
    
    Credentials are loaded from environment variables.
    In production, replace with database lookup.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        True if authentication successful, False otherwise
    """
    demo_user = get_demo_user()
    
    if username != demo_user["username"]:
        return False
    
    if not verify_password(password, demo_user["password_hash"]):
        return False
    
    return True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate JWT token and return the current user.
    
    This function is used as a dependency in protected routes.
    
    Args:
        credentials: HTTP Authorization credentials containing the JWT token
        
    Returns:
        Username from the token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    return username
