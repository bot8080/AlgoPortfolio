"""Service layer for portfolio operations.

Provides high-level portfolio operations with automatic
portfolio creation and user-friendly interface.
"""

from decimal import Decimal
from typing import List, Optional

from models.portfolio import Portfolio, Holding
from services.database.portfolio_repo import PortfolioRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioService:
    """Service for portfolio operations.

    Wraps PortfolioRepository with user-friendly operations
    that auto-create portfolios when needed.
    """

    def __init__(self, repository: PortfolioRepository):
        """Initialize service with repository.

        Args:
            repository: PortfolioRepository instance
        """
        self._repo = repository

    async def get_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Get user's portfolio.

        Args:
            user_id: Telegram user ID

        Returns:
            Portfolio if exists, None otherwise
        """
        return await self._repo.get_portfolio(user_id)

    async def get_holdings(self, user_id: int) -> List[Holding]:
        """Get all holdings for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of holdings (empty if no portfolio)
        """
        portfolio = await self._repo.get_portfolio(user_id)
        if not portfolio:
            return []
        return await self._repo.get_holdings(portfolio.id)

    async def add_holding(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        purchase_price: Decimal,
    ) -> Holding:
        """Add a stock holding to user's portfolio.

        Creates portfolio if it doesn't exist.

        Args:
            user_id: Telegram user ID
            symbol: Stock symbol (will be uppercased)
            quantity: Number of shares
            purchase_price: Price per share

        Returns:
            Created or updated Holding
        """
        # Get or create portfolio
        portfolio = await self._repo.get_or_create_portfolio(user_id)

        # Add the holding
        holding = await self._repo.add_holding(
            portfolio_id=portfolio.id,
            symbol=symbol.upper(),
            quantity=float(quantity),
            price=float(purchase_price),
        )

        logger.info(
            f"User {user_id} added {quantity} {symbol} @ ${purchase_price:.2f}"
        )
        return holding

    async def sell_holding(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        sell_price: Decimal,
    ) -> Optional[Holding]:
        """Sell shares from a holding.

        Args:
            user_id: Telegram user ID
            symbol: Stock symbol
            quantity: Number of shares to sell
            sell_price: Price per share

        Returns:
            Updated Holding, or None if holding not found

        Raises:
            ValueError: If selling more shares than owned
        """
        portfolio = await self._repo.get_portfolio(user_id)
        if not portfolio:
            return None

        holding = await self._repo.get_holding_by_symbol(portfolio.id, symbol)
        if not holding:
            return None

        if float(quantity) > holding.quantity:
            raise ValueError(
                f"Cannot sell {quantity} shares. You only own {holding.quantity}."
            )

        # Calculate new quantity
        new_quantity = holding.quantity - float(quantity)

        # Update or remove holding
        if new_quantity <= 0:
            await self._repo.remove_holding(holding.id)
            new_quantity = 0
        else:
            await self._repo.update_holding(
                holding.id, new_quantity, holding.avg_cost
            )

        # Record the sell transaction
        from models.portfolio import TransactionType
        await self._repo.record_transaction(
            holding.id,
            TransactionType.SELL,
            float(quantity),
            float(sell_price),
        )

        logger.info(
            f"User {user_id} sold {quantity} {symbol} @ ${sell_price:.2f}"
        )

        # Return updated holding info
        return Holding(
            id=holding.id,
            portfolio_id=portfolio.id,
            symbol=symbol.upper(),
            quantity=new_quantity,
            avg_cost=holding.avg_cost,
            created_at=holding.created_at,
        )

    async def get_transactions(
        self, user_id: int, limit: int = 50
    ) -> List[tuple]:
        """Get all transactions for a user.

        Args:
            user_id: Telegram user ID
            limit: Maximum transactions to return

        Returns:
            List of (Transaction, symbol) tuples
        """
        portfolio = await self._repo.get_portfolio(user_id)
        if not portfolio:
            return []
        return await self._repo.get_all_transactions(portfolio.id, limit)
