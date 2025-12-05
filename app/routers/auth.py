"""
Authentication router.

Handles user login and token generation.
"""

from fastapi import APIRouter, HTTPException, status

from app.auth import authenticate_user, create_access_token
from app.models import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    description="Authenticate with username and password to receive a JWT token"
)
async def login(request: LoginRequest) -> Token:
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login credentials (username and password)
        
    Returns:
        Token object with access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": request.username})
    
    return Token(access_token=access_token, token_type="bearer")
