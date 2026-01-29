"""Base class for market data providers."""

from abc import ABC, abstractmethod
from typing import Optional, List
from models.stock import StockPrice, StockInfo


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging and identification."""
        pass

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[StockPrice]:
        """
        Get current price for a stock symbol.

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            StockPrice object or None if not found
        """
        pass

    @abstractmethod
    async def get_info(self, symbol: str) -> Optional[StockInfo]:
        """
        Get company information for a stock symbol.

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            StockInfo object or None if not found
        """
        pass

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """
        Search for stocks by name or symbol.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of search results
        """
        # Default implementation - override in subclasses if supported
        return []

    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and responding.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to fetch a known symbol
            result = await self.get_price("AAPL")
            return result is not None
        except Exception:
            return False
