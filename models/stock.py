"""Stock data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class Recommendation(Enum):
    """Stock recommendation levels."""
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"


@dataclass
class StockPrice:
    """Current stock price data."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    currency: str = "USD"

    @property
    def is_positive(self) -> bool:
        """Check if price change is positive."""
        return self.change >= 0

    @property
    def formatted_change(self) -> str:
        """Format change with sign and percentage."""
        sign = "+" if self.is_positive else ""
        return f"{sign}{self.change:.2f} ({sign}{self.change_percent:.2f}%)"


@dataclass
class StockInfo:
    """Company information and fundamentals."""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    average_volume: Optional[int] = None
    description: Optional[str] = None

    @property
    def formatted_market_cap(self) -> str:
        """Format market cap in human-readable form."""
        if not self.market_cap:
            return "N/A"

        if self.market_cap >= 1_000_000_000_000:
            return f"${self.market_cap / 1_000_000_000_000:.2f}T"
        elif self.market_cap >= 1_000_000_000:
            return f"${self.market_cap / 1_000_000_000:.2f}B"
        elif self.market_cap >= 1_000_000:
            return f"${self.market_cap / 1_000_000:.2f}M"
        else:
            return f"${self.market_cap:,.0f}"


@dataclass
class AnalysisResult:
    """Stock analysis result with recommendation."""
    symbol: str
    price: StockPrice
    info: StockInfo
    recommendation: Recommendation
    confidence: float  # 0-100
    summary: str

    # Technical indicators (for future expansion)
    rsi: Optional[float] = None
    macd: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None

    @property
    def confidence_emoji(self) -> str:
        """Get emoji representation of confidence level."""
        if self.confidence >= 80:
            return "🟢"
        elif self.confidence >= 60:
            return "🟡"
        else:
            return "🔴"
