"""Database connection manager for SQLite."""

import aiosqlite
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from utils.logger import get_logger
from utils.exceptions import DatabaseError

logger = get_logger(__name__)

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "portfolio.db"


class DatabaseManager:
    """Async SQLite database connection manager."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file. Defaults to data/portfolio.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._connection: Optional[aiosqlite.Connection] = None

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection as async context manager.

        Yields:
            aiosqlite.Connection: Active database connection

        Example:
            async with db_manager.get_connection() as conn:
                await conn.execute("SELECT * FROM portfolios")
        """
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()

    async def init_tables(self) -> None:
        """Initialize database tables.

        Creates portfolios, holdings, and transactions tables if they don't exist.
        Also creates indexes for foreign keys.
        """
        logger.info(f"Initializing database at {self.db_path}")

        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        async with self.get_connection() as conn:
            try:
                # Create portfolios table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS portfolios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_user_id INTEGER UNIQUE NOT NULL,
                        name TEXT NOT NULL DEFAULT 'My Portfolio',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create holdings table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS holdings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        portfolio_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        quantity REAL NOT NULL DEFAULT 0,
                        avg_cost REAL NOT NULL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
                            ON DELETE CASCADE,
                        UNIQUE(portfolio_id, symbol)
                    )
                """)

                # Create transactions table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        holding_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL CHECK(
                            transaction_type IN ('BUY', 'SELL')
                        ),
                        quantity REAL NOT NULL,
                        price REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (holding_id) REFERENCES holdings(id)
                            ON DELETE CASCADE
                    )
                """)

                # Create indexes for foreign keys
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_id
                    ON holdings(portfolio_id)
                """)

                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_holding_id
                    ON transactions(holding_id)
                """)

                # Create index for user lookup
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_portfolios_user_id
                    ON portfolios(telegram_user_id)
                """)

                await conn.commit()
                logger.info("Database tables initialized successfully")

            except aiosqlite.Error as e:
                logger.error(f"Failed to initialize database: {e}")
                raise DatabaseError("table initialization", str(e))

    async def close(self) -> None:
        """Close any open connections."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")
