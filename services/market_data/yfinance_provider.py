"""YFinance market data provider."""

import asyncio
import random
from datetime import datetime
from typing import Optional
import yfinance as yf

from services.market_data.base import MarketDataProvider
from models.stock import StockPrice, StockInfo
from utils.exceptions import SymbolNotFoundError, DataFetchError
from utils.logger import get_logger

logger = get_logger(__name__)

# Retry settings for rate limiting
MAX_RETRIES = 3
BASE_DELAY = 2.0  # seconds


class YFinanceProvider(MarketDataProvider):
    """Market data provider using YFinance."""

    @property
    def name(self) -> str:
        return "YFinance"

    async def _fetch_ticker_info(self, symbol: str) -> dict:
        """Fetch ticker info with retry logic for rate limiting."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                loop = asyncio.get_event_loop()
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                info = await loop.run_in_executor(None, lambda: ticker.info)
                return info
            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if it's a rate limit error
                if "429" in str(e) or "too many requests" in error_str:
                    if attempt < MAX_RETRIES - 1:
                        # Exponential backoff with jitter
                        delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"Rate limited, retrying in {delay:.1f}s "
                            f"(attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                        await asyncio.sleep(delay)
                        continue
                raise

        raise last_error

    async def get_price(self, symbol: str) -> Optional[StockPrice]:
        """
        Get current price for a stock symbol.

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            StockPrice object or None if not found
        """
        try:
            info = await self._fetch_ticker_info(symbol)

            if not info or "symbol" not in info:
                logger.warning(f"Symbol not found: {symbol}")
                raise SymbolNotFoundError(symbol)

            # Handle both stocks and ETFs
            # ETFs use regularMarketPrice, stocks use currentPrice
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

            if not current_price:
                logger.warning(f"No price data for: {symbol}")
                raise DataFetchError(self.name, f"No price data for {symbol}")

            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0

            return StockPrice(
                symbol=symbol.upper(),
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=info.get("volume", 0) or 0,
                timestamp=datetime.now(),
                currency=info.get("currency", "USD"),
            )

        except SymbolNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise DataFetchError(self.name, str(e))

    async def get_info(self, symbol: str) -> Optional[StockInfo]:
        """
        Get company information for a stock symbol.

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            StockInfo object or None if not found
        """
        try:
            info = await self._fetch_ticker_info(symbol)

            if not info or "symbol" not in info:
                raise SymbolNotFoundError(symbol)

            return StockInfo(
                symbol=symbol.upper(),
                name=info.get("longName") or info.get("shortName", symbol),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
                eps=info.get("trailingEps"),
                dividend_yield=info.get("dividendYield"),
                fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                average_volume=info.get("averageVolume"),
                description=info.get("longBusinessSummary"),
            )

        except SymbolNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            raise DataFetchError(self.name, str(e))
