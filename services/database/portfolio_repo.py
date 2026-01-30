"""Repository for portfolio database operations."""

from datetime import datetime
from typing import List, Optional

import aiosqlite

from models.portfolio import Portfolio, Holding, Transaction, TransactionType
from services.database.connection import DatabaseManager
from utils.logger import get_logger
from utils.exceptions import DatabaseError

logger = get_logger(__name__)


class PortfolioRepository:
    """Repository for portfolio CRUD operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance for connections
        """
        self._db = db_manager

    # Portfolio operations

    async def create_portfolio(
        self, user_id: int, name: str = "My Portfolio"
    ) -> Portfolio:
        """Create a new portfolio for a user.

        Args:
            user_id: Telegram user ID
            name: Portfolio name

        Returns:
            Created Portfolio object

        Raises:
            DatabaseError: If creation fails
        """
        async with self._db.get_connection() as conn:
            try:
                cursor = await conn.execute(
                    """
                    INSERT INTO portfolios (telegram_user_id, name)
                    VALUES (?, ?)
                    """,
                    (user_id, name),
                )
                await conn.commit()

                portfolio_id = cursor.lastrowid
                logger.info(f"Created portfolio {portfolio_id} for user {user_id}")

                return Portfolio(
                    id=portfolio_id,
                    telegram_user_id=user_id,
                    name=name,
                    created_at=datetime.now(),
                )

            except aiosqlite.IntegrityError:
                # User already has a portfolio, fetch it
                return await self.get_portfolio(user_id)

            except aiosqlite.Error as e:
                logger.error(f"Failed to create portfolio: {e}")
                raise DatabaseError("create portfolio", str(e))

    async def get_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Get a user's portfolio.

        Args:
            user_id: Telegram user ID

        Returns:
            Portfolio if found, None otherwise
        """
        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT id, telegram_user_id, name, created_at
                FROM portfolios
                WHERE telegram_user_id = ?
                """,
                (user_id,),
            )
            row = await cursor.fetchone()

            if row:
                return Portfolio(
                    id=row["id"],
                    telegram_user_id=row["telegram_user_id"],
                    name=row["name"],
                    created_at=datetime.fromisoformat(row["created_at"])
                    if isinstance(row["created_at"], str)
                    else row["created_at"],
                )
            return None

    async def get_or_create_portfolio(
        self, user_id: int, name: str = "My Portfolio"
    ) -> Portfolio:
        """Get existing portfolio or create a new one.

        Args:
            user_id: Telegram user ID
            name: Portfolio name (used if creating new)

        Returns:
            Portfolio object
        """
        portfolio = await self.get_portfolio(user_id)
        if portfolio:
            return portfolio
        return await self.create_portfolio(user_id, name)

    # Holding operations

    async def add_holding(
        self, portfolio_id: int, symbol: str, quantity: float, price: float
    ) -> Holding:
        """Add a new holding or update existing one.

        If the symbol already exists, updates quantity and recalculates avg_cost.

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock symbol (uppercase)
            quantity: Number of shares
            price: Purchase price per share

        Returns:
            Created or updated Holding object

        Raises:
            DatabaseError: If operation fails
        """
        symbol = symbol.upper()

        async with self._db.get_connection() as conn:
            try:
                # Check if holding exists
                existing = await self.get_holding_by_symbol(portfolio_id, symbol)

                if existing:
                    # Update existing holding with new average cost
                    new_quantity = existing.quantity + quantity
                    new_avg_cost = (
                        (existing.total_cost + (quantity * price)) / new_quantity
                    )

                    await conn.execute(
                        """
                        UPDATE holdings
                        SET quantity = ?, avg_cost = ?
                        WHERE id = ?
                        """,
                        (new_quantity, new_avg_cost, existing.id),
                    )
                    await conn.commit()

                    holding = Holding(
                        id=existing.id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        quantity=new_quantity,
                        avg_cost=new_avg_cost,
                        created_at=existing.created_at,
                    )
                    logger.info(f"Updated holding {symbol}: qty={new_quantity}")

                else:
                    # Create new holding
                    cursor = await conn.execute(
                        """
                        INSERT INTO holdings (portfolio_id, symbol, quantity, avg_cost)
                        VALUES (?, ?, ?, ?)
                        """,
                        (portfolio_id, symbol, quantity, price),
                    )
                    await conn.commit()

                    holding = Holding(
                        id=cursor.lastrowid,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        quantity=quantity,
                        avg_cost=price,
                        created_at=datetime.now(),
                    )
                    logger.info(f"Created holding {symbol}: qty={quantity}")

                # Record the buy transaction
                await self.record_transaction(
                    holding.id, TransactionType.BUY, quantity, price
                )

                return holding

            except aiosqlite.Error as e:
                logger.error(f"Failed to add holding: {e}")
                raise DatabaseError("add holding", str(e))

    async def update_holding(
        self, holding_id: int, quantity: float, avg_cost: float
    ) -> Holding:
        """Update a holding's quantity and average cost.

        Args:
            holding_id: Holding ID
            quantity: New quantity
            avg_cost: New average cost

        Returns:
            Updated Holding object

        Raises:
            DatabaseError: If update fails
        """
        async with self._db.get_connection() as conn:
            try:
                await conn.execute(
                    """
                    UPDATE holdings
                    SET quantity = ?, avg_cost = ?
                    WHERE id = ?
                    """,
                    (quantity, avg_cost, holding_id),
                )
                await conn.commit()

                # Fetch updated holding
                cursor = await conn.execute(
                    """
                    SELECT id, portfolio_id, symbol, quantity, avg_cost, created_at
                    FROM holdings
                    WHERE id = ?
                    """,
                    (holding_id,),
                )
                row = await cursor.fetchone()

                if not row:
                    raise DatabaseError("update holding", "Holding not found")

                logger.info(f"Updated holding {holding_id}: qty={quantity}")
                return Holding(
                    id=row["id"],
                    portfolio_id=row["portfolio_id"],
                    symbol=row["symbol"],
                    quantity=row["quantity"],
                    avg_cost=row["avg_cost"],
                    created_at=datetime.fromisoformat(row["created_at"])
                    if isinstance(row["created_at"], str)
                    else row["created_at"],
                )

            except aiosqlite.Error as e:
                logger.error(f"Failed to update holding: {e}")
                raise DatabaseError("update holding", str(e))

    async def get_holdings(self, portfolio_id: int) -> List[Holding]:
        """Get all holdings for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of Holding objects
        """
        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT id, portfolio_id, symbol, quantity, avg_cost, created_at
                FROM holdings
                WHERE portfolio_id = ? AND quantity > 0
                ORDER BY symbol
                """,
                (portfolio_id,),
            )
            rows = await cursor.fetchall()

            return [
                Holding(
                    id=row["id"],
                    portfolio_id=row["portfolio_id"],
                    symbol=row["symbol"],
                    quantity=row["quantity"],
                    avg_cost=row["avg_cost"],
                    created_at=datetime.fromisoformat(row["created_at"])
                    if isinstance(row["created_at"], str)
                    else row["created_at"],
                )
                for row in rows
            ]

    async def get_holding_by_symbol(
        self, portfolio_id: int, symbol: str
    ) -> Optional[Holding]:
        """Get a specific holding by symbol.

        Args:
            portfolio_id: Portfolio ID
            symbol: Stock symbol

        Returns:
            Holding if found, None otherwise
        """
        symbol = symbol.upper()

        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT id, portfolio_id, symbol, quantity, avg_cost, created_at
                FROM holdings
                WHERE portfolio_id = ? AND symbol = ?
                """,
                (portfolio_id, symbol),
            )
            row = await cursor.fetchone()

            if row:
                return Holding(
                    id=row["id"],
                    portfolio_id=row["portfolio_id"],
                    symbol=row["symbol"],
                    quantity=row["quantity"],
                    avg_cost=row["avg_cost"],
                    created_at=datetime.fromisoformat(row["created_at"])
                    if isinstance(row["created_at"], str)
                    else row["created_at"],
                )
            return None

    async def remove_holding(self, holding_id: int) -> bool:
        """Remove a holding (set quantity to 0).

        Args:
            holding_id: Holding ID

        Returns:
            True if removed, False if not found
        """
        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                UPDATE holdings SET quantity = 0 WHERE id = ?
                """,
                (holding_id,),
            )
            await conn.commit()
            return cursor.rowcount > 0

    # Transaction operations

    async def record_transaction(
        self,
        holding_id: int,
        transaction_type: TransactionType,
        quantity: float,
        price: float,
    ) -> Transaction:
        """Record a buy or sell transaction.

        Args:
            holding_id: Holding ID
            transaction_type: BUY or SELL
            quantity: Number of shares
            price: Price per share

        Returns:
            Created Transaction object

        Raises:
            DatabaseError: If recording fails
        """
        async with self._db.get_connection() as conn:
            try:
                cursor = await conn.execute(
                    """
                    INSERT INTO transactions (holding_id, transaction_type, quantity, price)
                    VALUES (?, ?, ?, ?)
                    """,
                    (holding_id, transaction_type.value, quantity, price),
                )
                await conn.commit()

                logger.info(
                    f"Recorded {transaction_type.value}: "
                    f"{quantity} shares @ ${price:.2f}"
                )

                return Transaction(
                    id=cursor.lastrowid,
                    holding_id=holding_id,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=price,
                    timestamp=datetime.now(),
                )

            except aiosqlite.Error as e:
                logger.error(f"Failed to record transaction: {e}")
                raise DatabaseError("record transaction", str(e))

    async def get_transactions(
        self, holding_id: int, limit: int = 50
    ) -> List[Transaction]:
        """Get transactions for a holding.

        Args:
            holding_id: Holding ID
            limit: Maximum number of transactions to return

        Returns:
            List of Transaction objects, most recent first
        """
        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT id, holding_id, transaction_type, quantity, price, timestamp
                FROM transactions
                WHERE holding_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (holding_id, limit),
            )
            rows = await cursor.fetchall()

            return [
                Transaction(
                    id=row["id"],
                    holding_id=row["holding_id"],
                    transaction_type=TransactionType(row["transaction_type"]),
                    quantity=row["quantity"],
                    price=row["price"],
                    timestamp=datetime.fromisoformat(row["timestamp"])
                    if isinstance(row["timestamp"], str)
                    else row["timestamp"],
                )
                for row in rows
            ]

    async def get_all_transactions(
        self, portfolio_id: int, limit: int = 100
    ) -> List[tuple]:
        """Get all transactions for a portfolio with holding info.

        Args:
            portfolio_id: Portfolio ID
            limit: Maximum number of transactions

        Returns:
            List of (Transaction, symbol) tuples
        """
        async with self._db.get_connection() as conn:
            cursor = await conn.execute(
                """
                SELECT t.id, t.holding_id, t.transaction_type, t.quantity,
                       t.price, t.timestamp, h.symbol
                FROM transactions t
                JOIN holdings h ON t.holding_id = h.id
                WHERE h.portfolio_id = ?
                ORDER BY t.timestamp DESC
                LIMIT ?
                """,
                (portfolio_id, limit),
            )
            rows = await cursor.fetchall()

            return [
                (
                    Transaction(
                        id=row["id"],
                        holding_id=row["holding_id"],
                        transaction_type=TransactionType(row["transaction_type"]),
                        quantity=row["quantity"],
                        price=row["price"],
                        timestamp=datetime.fromisoformat(row["timestamp"])
                        if isinstance(row["timestamp"], str)
                        else row["timestamp"],
                    ),
                    row["symbol"],
                )
                for row in rows
            ]
