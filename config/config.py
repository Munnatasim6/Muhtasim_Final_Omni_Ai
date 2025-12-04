import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "OmniTrade AI Core"
    VERSION: str = "1.0.0"
    ENV: str = Field(default="development", description="Environment: development, production")
    API_KEY: str = Field(default="secret-key", description="Master API Key for internal services")

    # Database (TimescaleDB)
    DB_HOST: str = Field(default="localhost", description="Database Host")
    DB_PORT: int = Field(default=5432, description="Database Port")
    DB_USER: str = Field(default="postgres", description="Database User")
    DB_PASSWORD: str = Field(default="password", description="Database Password")
    DB_NAME: str = Field(default="omnitrade", description="Database Name")

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis Host")
    REDIS_PORT: int = Field(default=6379, description="Redis Port")
    REDIS_DB: int = Field(default=0, description="Redis DB Index")

    # Exchange Keys (CEX)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPACA_ENDPOINT: str = "https://paper-api.alpaca.markets"

    # Web3 / DeFi
    INFURA_URL: Optional[str] = None
    WALLET_ADDRESS: Optional[str] = None
    PRIVATE_KEY: Optional[str] = None

    # Macro / News
    FRED_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # Notifications
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Model Settings
    MODEL_PATH: str = "models/"
    RETRAIN_INTERVAL_HOURS: int = 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
