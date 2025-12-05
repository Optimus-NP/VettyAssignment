"""
Service layer for interacting with external APIs.

Handles communication with CoinGecko API and data transformation.
"""

from typing import Dict, List, Optional

import requests
from fastapi import HTTPException, status

from app.config import settings
from app.models import Category, CoinBase, CoinDetail


class CoinGeckoService:
    """
    Service for interacting with CoinGecko API.
    
    Provides methods to fetch coins, categories, and market data.
    """
    
    def __init__(self):
        """Initialize the CoinGecko service."""
        self.base_url = settings.coingecko_api_base_url
        self.timeout = settings.coingecko_api_timeout
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make an HTTP request to CoinGecko API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Prepare headers with API key if available
        headers = {}
        if settings.coingecko_api_key:
            headers["x-cg-demo-api-key"] = settings.coingecko_api_key
        
        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="CoinGecko API timeout"
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"CoinGecko API error: {str(e)}"
            )
    
    def get_coins_list(self) -> List[CoinBase]:
        """
        Get list of all coins with id, symbol, and name.
        
        Returns:
            List of CoinBase objects
        """
        data = self._make_request("coins/list")
        
        return [
            CoinBase(
                id=coin["id"],
                symbol=coin["symbol"],
                name=coin["name"]
            )
            for coin in data
        ]
    
    def get_categories_list(self) -> List[Category]:
        """
        Get list of all coin categories.
        
        Returns:
            List of Category objects
        """
        data = self._make_request("coins/categories/list")
        
        return [
            Category(
                category_id=category["category_id"],
                name=category["name"]
            )
            for category in data
        ]
    
    def get_coins_markets(
        self,
        vs_currency: str = "inr",
        category: Optional[str] = None,
        ids: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> List[Dict]:
        """
        Get coins market data with pagination.
        
        Args:
            vs_currency: Currency to get price in (inr or cad)
            category: Filter by category
            ids: Comma-separated coin IDs to filter
            page: Page number
            per_page: Items per page
            
        Returns:
            List of market data dictionaries
        """
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": False
        }
        
        if category:
            params["category"] = category
        
        if ids:
            params["ids"] = ids
        
        return self._make_request("coins/markets", params)
    
    def get_coin_details_with_market_data(
        self,
        coin_ids: Optional[List[str]] = None,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> List[CoinDetail]:
        """
        Get detailed coin information with market data in INR and CAD.
        
        Args:
            coin_ids: List of coin IDs to fetch
            category: Category to filter by
            page: Page number
            per_page: Items per page
            
        Returns:
            List of CoinDetail objects with both INR and CAD prices
        """
        # Convert coin_ids list to comma-separated string
        ids_param = ",".join(coin_ids) if coin_ids else None
        
        # Fetch data in INR
        inr_data = self.get_coins_markets(
            vs_currency="inr",
            category=category,
            ids=ids_param,
            page=page,
            per_page=per_page
        )
        
        # Fetch data in CAD
        cad_data = self.get_coins_markets(
            vs_currency="cad",
            category=category,
            ids=ids_param,
            page=page,
            per_page=per_page
        )
        
        # Create a mapping of CAD data by coin ID
        cad_map = {coin["id"]: coin for coin in cad_data}
        
        # Combine data from both currencies
        results = []
        for inr_coin in inr_data:
            cad_coin = cad_map.get(inr_coin["id"], {})
            
            coin_detail = CoinDetail(
                id=inr_coin["id"],
                symbol=inr_coin["symbol"],
                name=inr_coin["name"],
                current_price_inr=inr_coin.get("current_price"),
                current_price_cad=cad_coin.get("current_price"),
                market_cap_inr=inr_coin.get("market_cap"),
                market_cap_cad=cad_coin.get("market_cap"),
                total_volume_inr=inr_coin.get("total_volume"),
                total_volume_cad=cad_coin.get("total_volume"),
                price_change_percentage_24h=inr_coin.get(
                    "price_change_percentage_24h"
                ),
                market_cap_rank=inr_coin.get("market_cap_rank")
            )
            results.append(coin_detail)
        
        return results
    
    def check_health(self) -> bool:
        """
        Check if CoinGecko API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            self._make_request("ping")
            return True
        except HTTPException:
            return False


# Global service instance
coingecko_service = CoinGeckoService()
