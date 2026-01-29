"""Shared pytest fixtures for AlgoPortfolio tests."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from models.stock import StockPrice, StockInfo, AnalysisResult, Recommendation
from services.market_data.yfinance_provider import YFinanceProvider


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


# =============================================================================
# Model Fixtures
# =============================================================================

@pytest.fixture
def sample_stock_price():
    """Create a sample StockPrice for testing."""
    return StockPrice(
        symbol="AAPL",
        price=150.25,
        change=2.50,
        change_percent=1.69,
        volume=50_000_000,
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
        currency="USD",
    )


@pytest.fixture
def sample_stock_price_negative():
    """Create a sample StockPrice with negative change."""
    return StockPrice(
        symbol="TSLA",
        price=245.00,
        change=-5.75,
        change_percent=-2.29,
        volume=30_000_000,
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
        currency="USD",
    )


@pytest.fixture
def sample_stock_info():
    """Create a sample StockInfo for testing."""
    return StockInfo(
        symbol="AAPL",
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=2_500_000_000_000,  # 2.5T
        pe_ratio=28.5,
        eps=6.05,
        dividend_yield=0.0041,  # 0.41%
        fifty_two_week_high=199.62,
        fifty_two_week_low=124.17,
        average_volume=55_000_000,
        description="Apple Inc. designs, manufactures, and markets smartphones...",
    )


@pytest.fixture
def sample_stock_info_minimal():
    """Create a StockInfo with minimal data (like an ETF)."""
    return StockInfo(
        symbol="SPY",
        name="SPDR S&P 500 ETF Trust",
        sector=None,
        industry=None,
        market_cap=None,
        pe_ratio=None,
        eps=None,
        dividend_yield=None,
        fifty_two_week_high=None,
        fifty_two_week_low=None,
        average_volume=None,
        description=None,
    )


@pytest.fixture
def sample_analysis_result(sample_stock_price, sample_stock_info):
    """Create a sample AnalysisResult for testing."""
    return AnalysisResult(
        symbol="AAPL",
        price=sample_stock_price,
        info=sample_stock_info,
        recommendation=Recommendation.BUY,
        confidence=75.0,
        summary="Strong fundamentals with positive momentum.",
    )


# =============================================================================
# Provider Fixtures
# =============================================================================

@pytest.fixture
def provider():
    """Create YFinance provider instance."""
    return YFinanceProvider()


@pytest.fixture
def mock_provider():
    """Create a mocked YFinanceProvider."""
    mock = MagicMock(spec=YFinanceProvider)
    mock.get_price = AsyncMock()
    mock.get_info = AsyncMock()
    mock.health_check = AsyncMock(return_value=True)
    return mock


# =============================================================================
# Telegram Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock()

    # Mock user
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"

    # Mock message
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()

    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.args = []
    context.bot = MagicMock()
    return context


@pytest.fixture
def mock_status_message():
    """Create a mock status message that can be edited."""
    msg = MagicMock()
    msg.edit_text = AsyncMock()
    return msg


# =============================================================================
# Helper Functions
# =============================================================================

def create_stock_price(
    symbol: str = "AAPL",
    price: float = 150.0,
    change: float = 2.0,
    change_percent: float = 1.35,
    volume: int = 50_000_000,
) -> StockPrice:
    """Factory function to create StockPrice with custom values."""
    return StockPrice(
        symbol=symbol,
        price=price,
        change=change,
        change_percent=change_percent,
        volume=volume,
        timestamp=datetime.now(),
        currency="USD",
    )


def create_stock_info(
    symbol: str = "AAPL",
    name: str = "Apple Inc.",
    market_cap: float = 2_500_000_000_000,
    pe_ratio: float = 28.5,
) -> StockInfo:
    """Factory function to create StockInfo with custom values."""
    return StockInfo(
        symbol=symbol,
        name=name,
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=market_cap,
        pe_ratio=pe_ratio,
        eps=6.05,
        dividend_yield=0.0041,
        fifty_two_week_high=199.62,
        fifty_two_week_low=124.17,
        average_volume=55_000_000,
    )
