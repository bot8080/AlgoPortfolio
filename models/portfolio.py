"""Portfolio data models for tracking holdings and transactions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionType(Enum):
    """Type of portfolio transaction."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Portfolio:
    """User's stock portfolio."""
    telegram_user_id: int
    name: str = "My Portfolio"
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"Portfolio({self.name}, user={self.telegram_user_id})"


@dataclass
class Holding:
    """A stock holding within a portfolio."""
    portfolio_id: int
    symbol: str
    quantity: float
    avg_cost: float
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_cost(self) -> float:
        """Calculate total cost basis for this holding."""
        return self.quantity * self.avg_cost

    @property
    def formatted_quantity(self) -> str:
        """Format quantity, showing decimals only if needed."""
        if self.quantity == int(self.quantity):
            return str(int(self.quantity))
        return f"{self.quantity:.4f}".rstrip("0").rstrip(".")

    def __str__(self) -> str:
        return f"Holding({self.symbol}, qty={self.formatted_quantity})"


@dataclass
class Transaction:
    """A buy or sell transaction for a holding."""
    holding_id: int
    transaction_type: TransactionType
    quantity: float
    price: float
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_value(self) -> float:
        """Calculate total transaction value."""
        return self.quantity * self.price

    @property
    def type_emoji(self) -> str:
        """Get emoji for transaction type."""
        return "🟢" if self.transaction_type == TransactionType.BUY else "🔴"

    def __str__(self) -> str:
        return (
            f"Transaction({self.transaction_type.value}, "
            f"{self.quantity}@${self.price:.2f})"
        )
