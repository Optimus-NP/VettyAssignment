"""
Pydantic models for API requests and responses.

Defines data structures for authentication, coins, categories, and pagination.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT token response model."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class LoginRequest(BaseModel):
    """Login request model."""
    
    username: str = Field(..., description="Username", min_length=1)
    password: str = Field(..., description="Password", min_length=1)


class CoinBase(BaseModel):
    """Base coin model with basic information."""
    
    id: str = Field(..., description="Coin ID")
    symbol: str = Field(..., description="Coin symbol")
    name: str = Field(..., description="Coin name")


class CoinDetail(CoinBase):
    """Detailed coin model with market data."""
    
    current_price_inr: Optional[float] = Field(
        None, description="Current price in INR"
    )
    current_price_cad: Optional[float] = Field(
        None, description="Current price in CAD"
    )
    market_cap_inr: Optional[float] = Field(
        None, description="Market cap in INR"
    )
    market_cap_cad: Optional[float] = Field(
        None, description="Market cap in CAD"
    )
    total_volume_inr: Optional[float] = Field(
        None, description="24h volume in INR"
    )
    total_volume_cad: Optional[float] = Field(
        None, description="24h volume in CAD"
    )
    price_change_percentage_24h: Optional[float] = Field(
        None, description="24h price change percentage"
    )
    market_cap_rank: Optional[int] = Field(
        None, description="Market cap rank"
    )


class Category(BaseModel):
    """Coin category model."""
    
    category_id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    
    data: List[Any] = Field(..., description="List of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")


class HealthCheck(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    coingecko_status: str = Field(..., description="CoinGecko API status")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
