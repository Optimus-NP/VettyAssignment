"""
Configuration management for the application.

This module handles loading and validating configuration from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses pydantic-settings for validation and type conversion.
    """
    
    # API Configuration
    api_version: str = "1.0.0"
    api_title: str = "Cryptocurrency Market API"
    api_description: str = "REST API for fetching cryptocurrency market updates"
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Demo User Credentials (for testing only, use database in production)
    demo_username: str = "demo"
    demo_password: str = "demo123"
    
    # CoinGecko API Configuration
    coingecko_api_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str = ""  # Optional: CoinGecko Demo API key
    coingecko_api_timeout: int = 30
    
    # Pagination Configuration
    default_page_size: int = 10
    max_page_size: int = 100
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        """Pydantic configuration class."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
