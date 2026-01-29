---
name: db-setup
description: Initialize SQLite database infrastructure for portfolio tracking. Creates connection manager, models, and repository pattern.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Database Setup Skill

Initialize SQLite database infrastructure for AlgoPortfolio portfolio tracking.

## Instructions

### Step 1: Update requirements.txt
Add `aiosqlite>=0.19.0` to requirements.txt if not present.

### Step 2: Create Database Directory Structure
```
services/database/
├── __init__.py
├── connection.py      # Async SQLite connection manager
└── portfolio_repo.py  # Portfolio repository with CRUD
```

### Step 3: Create Connection Manager
Create `services/database/connection.py`:
```python
"""Database connection management."""
import aiosqlite
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

class DatabaseManager:
    """Manage SQLite database connections."""

    def __init__(self, db_path: str = "data/portfolio.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection as async context manager."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()

    async def init_tables(self) -> None:
        """Initialize database tables."""
        async with self.get_connection() as conn:
            await conn.executescript('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL DEFAULT 'Default',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    avg_cost REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
                    UNIQUE(portfolio_id, symbol)
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    holding_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (holding_id) REFERENCES holdings(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(telegram_user_id);
                CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON holdings(portfolio_id);
                CREATE INDEX IF NOT EXISTS idx_transactions_holding ON transactions(holding_id);
            ''')
            await conn.commit()
```

### Step 4: Create Portfolio Models
Create/update `models/portfolio.py`:
```python
"""Portfolio data models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionType(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Portfolio:
    """User's stock portfolio."""
    telegram_user_id: int
    name: str = "Default"
    id: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class Holding:
    """A stock position in a portfolio."""
    portfolio_id: int
    symbol: str
    quantity: float
    avg_cost: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def total_cost(self) -> float:
        return self.quantity * self.avg_cost

@dataclass
class Transaction:
    """A buy or sell transaction."""
    holding_id: int
    transaction_type: TransactionType
    quantity: float
    price: float
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
```

### Step 5: Create Repository
Create `services/database/portfolio_repo.py` with async CRUD operations for portfolios, holdings, and transactions.

### Step 6: Create Data Directory
- Create `data/` directory
- Add `data/.gitkeep`
- Update `.gitignore` to include `data/*.db`

### Step 7: Create Package Exports
Create `services/database/__init__.py`:
```python
"""Database service package."""
from .connection import DatabaseManager
from .portfolio_repo import PortfolioRepository

__all__ = ["DatabaseManager", "PortfolioRepository"]
```

### Step 8: Verify
- Run `python -c "from services.database import DatabaseManager"` to verify imports
- Run tests if available

## Notes
- Uses aiosqlite for async SQLite operations
- Follows repository pattern for data access
- All database operations are async
- Tables use foreign keys with CASCADE delete
