"""
Coins router.

Handles cryptocurrency-related endpoints with pagination and authentication.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.config import settings
from app.models import Category, CoinBase, CoinDetail, PaginatedResponse
from app.services import coingecko_service

router = APIRouter(prefix="/v1/coins", tags=["Coins"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List all coins",
    description="Get paginated list of all available coins with their IDs"
)
async def list_coins(
    page_num: int = Query(
        1, ge=1, description="Page number (starts from 1)", alias="page_num"
    ),
    per_page: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Number of items per page"
    ),
    current_user: str = Depends(get_current_user)
) -> PaginatedResponse:
    """
    List all available coins with pagination.
    
    This endpoint requires authentication via JWT token.
    
    Args:
        page_num: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        current_user: Authenticated user (injected by dependency)
        
    Returns:
        Paginated response with coin data
    """
    # Get all coins from CoinGecko
    all_coins = coingecko_service.get_coins_list()
    total = len(all_coins)
    
    # Calculate pagination
    start_idx = (page_num - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice the data for current page
    paginated_coins = all_coins[start_idx:end_idx]
    
    return PaginatedResponse(
        data=paginated_coins,
        page=page_num,
        per_page=per_page,
        total=total
    )


@router.get(
    "/categories",
    response_model=PaginatedResponse,
    summary="List coin categories",
    description="Get paginated list of all coin categories"
)
async def list_categories(
    page_num: int = Query(
        1, ge=1, description="Page number (starts from 1)", alias="page_num"
    ),
    per_page: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Number of items per page"
    ),
    current_user: str = Depends(get_current_user)
) -> PaginatedResponse:
    """
    List all available coin categories with pagination.
    
    This endpoint requires authentication via JWT token.
    
    Args:
        page_num: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        current_user: Authenticated user (injected by dependency)
        
    Returns:
        Paginated response with category data
    """
    # Get all categories from CoinGecko
    all_categories = coingecko_service.get_categories_list()
    total = len(all_categories)
    
    # Calculate pagination
    start_idx = (page_num - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice the data for current page
    paginated_categories = all_categories[start_idx:end_idx]
    
    return PaginatedResponse(
        data=paginated_categories,
        page=page_num,
        per_page=per_page,
        total=total
    )


@router.get(
    "/market",
    response_model=PaginatedResponse,
    summary="Get coins with market data",
    description=(
        "Get coins with market data in INR and CAD. "
        "Filter by coin IDs or category."
    )
)
async def get_coins_market_data(
    coin_ids: Optional[str] = Query(
        None,
        description="Comma-separated list of coin IDs (e.g., bitcoin,ethereum)"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by category (e.g., decentralized-finance-defi)"
    ),
    page_num: int = Query(
        1, ge=1, description="Page number (starts from 1)", alias="page_num"
    ),
    per_page: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Number of items per page"
    ),
    current_user: str = Depends(get_current_user)
) -> PaginatedResponse:
    """
    Get coins with detailed market data in both INR and CAD.
    
    This endpoint requires authentication via JWT token.
    You can filter results by specific coin IDs or by category.
    
    Args:
        coin_ids: Comma-separated coin IDs to filter
        category: Category to filter by
        page_num: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        current_user: Authenticated user (injected by dependency)
        
    Returns:
        Paginated response with detailed coin market data
    """
    # Convert comma-separated string to list if provided
    coin_ids_list = None
    if coin_ids:
        coin_ids_list = [coin_id.strip() for coin_id in coin_ids.split(",")]
    
    # Get coin details with market data
    coins = coingecko_service.get_coin_details_with_market_data(
        coin_ids=coin_ids_list,
        category=category,
        page=page_num,
        per_page=per_page
    )
    
    # Note: For paginated API responses, we use the current page count
    # as the total since CoinGecko doesn't provide total count
    total = len(coins)
    
    return PaginatedResponse(
        data=coins,
        page=page_num,
        per_page=per_page,
        total=total
    )
