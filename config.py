"""Configuration management for AlgoPortfolio."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from utils.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Base paths
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # API Keys (optional for MVP)
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = str(LOGS_DIR / "algoportfolio.log")

    # Development
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Cache settings (for future use)
    CACHE_TTL_PRICE: int = int(os.getenv("CACHE_TTL_PRICE", "60"))  # seconds
    CACHE_TTL_INFO: int = int(os.getenv("CACHE_TTL_INFO", "3600"))  # seconds

    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration.

        Raises:
            ConfigurationError: If required config is missing
        """
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ConfigurationError(
                "TELEGRAM_BOT_TOKEN",
                "Bot token is required. Get one from @BotFather on Telegram.",
            )

        # Ensure logs directory exists
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.DEBUG

    @classmethod
    def get_log_level(cls) -> str:
        """Get logging level, higher in debug mode."""
        return "DEBUG" if cls.DEBUG else cls.LOG_LEVEL


# Validate on import
try:
    Config.validate()
except ConfigurationError as e:
    # Allow import to succeed for testing, but print warning
    import sys

    print(f"⚠️  Configuration warning: {e}", file=sys.stderr)
