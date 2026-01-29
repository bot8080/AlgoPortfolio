"""Tests for market data providers."""

import pytest
import asyncio
from services.market_data.yfinance_provider import YFinanceProvider
from utils.exceptions import SymbolNotFoundError


@pytest.fixture
def provider():
    """Create YFinance provider instance."""
    return YFinanceProvider()


@pytest.mark.asyncio
async def test_get_price_valid_symbol(provider):
    """Test fetching price for a valid symbol."""
    price = await provider.get_price("AAPL")

    assert price is not None
    assert price.symbol == "AAPL"
    assert price.price > 0
    assert price.currency == "USD"


@pytest.mark.asyncio
async def test_get_price_invalid_symbol(provider):
    """Test fetching price for an invalid symbol."""
    with pytest.raises(SymbolNotFoundError):
        await provider.get_price("INVALIDXYZ123")


@pytest.mark.asyncio
async def test_get_info_valid_symbol(provider):
    """Test fetching info for a valid symbol."""
    info = await provider.get_info("AAPL")

    assert info is not None
    assert info.symbol == "AAPL"
    assert info.name is not None
    assert "Apple" in info.name


@pytest.mark.asyncio
async def test_get_info_has_fundamentals(provider):
    """Test that info includes fundamental data."""
    info = await provider.get_info("MSFT")

    assert info.market_cap is not None
    assert info.market_cap > 0
    # P/E might be None for some stocks, so just check it's returned
    assert hasattr(info, "pe_ratio")


@pytest.mark.asyncio
async def test_etf_support(provider):
    """Test that ETFs are supported (use regularMarketPrice)."""
    price = await provider.get_price("SPY")

    assert price is not None
    assert price.symbol == "SPY"
    assert price.price > 0


@pytest.mark.asyncio
async def test_provider_health_check(provider):
    """Test provider health check."""
    is_healthy = await provider.health_check()
    assert is_healthy is True


if __name__ == "__main__":
    # Quick test without pytest
    async def quick_test():
        provider = YFinanceProvider()
        print("Testing YFinance Provider...")

        # Test AAPL
        price = await provider.get_price("AAPL")
        print(f"AAPL Price: ${price.price:.2f} ({price.formatted_change})")

        info = await provider.get_info("AAPL")
        print(f"AAPL: {info.name}")
        print(f"Market Cap: {info.formatted_market_cap}")
        print(f"P/E: {info.pe_ratio:.2f if info.pe_ratio else 'N/A'}")

        print("\nAll tests passed!")

    asyncio.run(quick_test())
