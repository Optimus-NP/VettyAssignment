"""
Tests for API routers.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.models import Category, CoinBase, CoinDetail


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    with patch("app.services.coingecko_service.check_health", return_value=True):
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["coingecko_status"] == "healthy"


def test_health_check_unhealthy_coingecko(client: TestClient):
    """Test health check when CoinGecko is unhealthy."""
    with patch("app.services.coingecko_service.check_health", return_value=False):
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["coingecko_status"] == "unhealthy"


def test_get_version(client: TestClient):
    """Test version endpoint."""
    response = client.get("/health/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "title" in data


def test_list_coins_success(client: TestClient, auth_headers: dict):
    """Test listing coins with authentication."""
    mock_coins = [
        CoinBase(id="bitcoin", symbol="btc", name="Bitcoin"),
        CoinBase(id="ethereum", symbol="eth", name="Ethereum")
    ]
    
    with patch(
        "app.services.coingecko_service.get_coins_list",
        return_value=mock_coins
    ):
        response = client.get("/v1/coins/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert data["total"] == 2


def test_list_coins_pagination(client: TestClient, auth_headers: dict):
    """Test coins pagination."""
    mock_coins = [
        CoinBase(id=f"coin{i}", symbol=f"c{i}", name=f"Coin {i}")
        for i in range(25)
    ]
    
    with patch(
        "app.services.coingecko_service.get_coins_list",
        return_value=mock_coins
    ):
        # Test page 1
        response = client.get(
            "/v1/coins/?page_num=1&per_page=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["page"] == 1
        
        # Test page 2
        response = client.get(
            "/v1/coins/?page_num=2&per_page=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["page"] == 2


def test_list_categories_success(client: TestClient, auth_headers: dict):
    """Test listing categories with authentication."""
    mock_categories = [
        Category(category_id="defi", name="DeFi"),
        Category(category_id="nft", name="NFT")
    ]
    
    with patch(
        "app.services.coingecko_service.get_categories_list",
        return_value=mock_categories
    ):
        response = client.get("/v1/coins/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["total"] == 2


def test_get_coins_market_data_success(client: TestClient, auth_headers: dict):
    """Test getting coins with market data."""
    mock_coins = [
        CoinDetail(
            id="bitcoin",
            symbol="btc",
            name="Bitcoin",
            current_price_inr=5000000.0,
            current_price_cad=75000.0,
            market_cap_inr=100000000000.0,
            market_cap_cad=1500000000.0,
            total_volume_inr=1000000000.0,
            total_volume_cad=15000000.0,
            price_change_percentage_24h=2.5,
            market_cap_rank=1
        )
    ]
    
    with patch(
        "app.services.coingecko_service.get_coin_details_with_market_data",
        return_value=mock_coins
    ):
        response = client.get("/v1/coins/market", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "bitcoin"
        assert data["data"][0]["current_price_inr"] == 5000000.0
        assert data["data"][0]["current_price_cad"] == 75000.0


def test_get_coins_market_data_with_filters(client: TestClient, auth_headers: dict):
    """Test getting coins with market data using filters."""
    mock_coins = [
        CoinDetail(
            id="bitcoin",
            symbol="btc",
            name="Bitcoin",
            current_price_inr=5000000.0,
            current_price_cad=75000.0
        )
    ]
    
    with patch(
        "app.services.coingecko_service.get_coin_details_with_market_data",
        return_value=mock_coins
    ) as mock_method:
        # Test with coin_ids filter
        response = client.get(
            "/v1/coins/market?coin_ids=bitcoin,ethereum",
            headers=auth_headers
        )
        assert response.status_code == 200
        mock_method.assert_called_once()
        call_args = mock_method.call_args[1]
        assert call_args["coin_ids"] == ["bitcoin", "ethereum"]
        
        # Test with category filter
        mock_method.reset_mock()
        response = client.get(
            "/v1/coins/market?category=defi",
            headers=auth_headers
        )
        assert response.status_code == 200
        mock_method.assert_called_once()
        call_args = mock_method.call_args[1]
        assert call_args["category"] == "defi"


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_coins_without_auth(client: TestClient):
    """Test accessing coins endpoint without authentication."""
    response = client.get("/v1/coins/")
    assert response.status_code == 403


def test_categories_without_auth(client: TestClient):
    """Test accessing categories endpoint without authentication."""
    response = client.get("/v1/coins/categories")
    assert response.status_code == 403


def test_market_without_auth(client: TestClient):
    """Test accessing market endpoint without authentication."""
    response = client.get("/v1/coins/market")
    assert response.status_code == 403
