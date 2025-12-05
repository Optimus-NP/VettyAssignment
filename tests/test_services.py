"""
Tests for service layer.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException

from app.services import CoinGeckoService


@pytest.fixture
def service():
    """Create a CoinGeckoService instance."""
    return CoinGeckoService()


def test_make_request_success(service):
    """Test successful API request."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    
    with patch("requests.get", return_value=mock_response):
        result = service._make_request("test_endpoint")
        assert result == {"data": "test"}


def test_make_request_timeout(service):
    """Test API request timeout."""
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(HTTPException) as exc_info:
            service._make_request("test_endpoint")
        assert exc_info.value.status_code == 504


def test_make_request_error(service):
    """Test API request error."""
    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Error")
    ):
        with pytest.raises(HTTPException) as exc_info:
            service._make_request("test_endpoint")
        assert exc_info.value.status_code == 503


def test_get_coins_list(service):
    """Test getting coins list."""
    mock_data = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum"}
    ]
    
    with patch.object(service, "_make_request", return_value=mock_data):
        result = service.get_coins_list()
        assert len(result) == 2
        assert result[0].id == "bitcoin"
        assert result[1].id == "ethereum"


def test_get_categories_list(service):
    """Test getting categories list."""
    mock_data = [
        {"category_id": "defi", "name": "DeFi"},
        {"category_id": "nft", "name": "NFT"}
    ]
    
    with patch.object(service, "_make_request", return_value=mock_data):
        result = service.get_categories_list()
        assert len(result) == 2
        assert result[0].category_id == "defi"
        assert result[1].category_id == "nft"


def test_get_coins_markets(service):
    """Test getting coins market data."""
    mock_data = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 5000000,
            "market_cap": 100000000000
        }
    ]
    
    with patch.object(service, "_make_request", return_value=mock_data):
        result = service.get_coins_markets(
            vs_currency="inr",
            page=1,
            per_page=10
        )
        assert len(result) == 1
        assert result[0]["id"] == "bitcoin"


def test_get_coin_details_with_market_data(service):
    """Test getting detailed coin data with both currencies."""
    inr_data = [{
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 5000000,
        "market_cap": 100000000000,
        "total_volume": 1000000000,
        "price_change_percentage_24h": 2.5,
        "market_cap_rank": 1
    }]
    
    cad_data = [{
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 75000,
        "market_cap": 1500000000,
        "total_volume": 15000000
    }]
    
    with patch.object(
        service,
        "get_coins_markets",
        side_effect=[inr_data, cad_data]
    ):
        result = service.get_coin_details_with_market_data(
            coin_ids=["bitcoin"],
            page=1,
            per_page=10
        )
        
        assert len(result) == 1
        assert result[0].id == "bitcoin"
        assert result[0].current_price_inr == 5000000
        assert result[0].current_price_cad == 75000


def test_check_health_success(service):
    """Test health check when API is healthy."""
    with patch.object(service, "_make_request", return_value={"status": "ok"}):
        assert service.check_health() is True


def test_check_health_failure(service):
    """Test health check when API is down."""
    with patch.object(
        service,
        "_make_request",
        side_effect=HTTPException(status_code=503, detail="Error")
    ):
        assert service.check_health() is False
