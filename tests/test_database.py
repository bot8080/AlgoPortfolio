"""Tests for database layer."""

import pytest
import pytest_asyncio
from pathlib import Path
import tempfile

from models.portfolio import Portfolio, Holding, Transaction, TransactionType
from services.database.connection import DatabaseManager
from services.database.portfolio_repo import PortfolioRepository


# Fixtures


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    # Cleanup after test
    try:
        path.unlink()
    except (FileNotFoundError, PermissionError):
        pass


@pytest_asyncio.fixture
async def db_manager(temp_db_path):
    """Create a DatabaseManager with temporary database."""
    manager = DatabaseManager(temp_db_path)
    await manager.init_tables()
    yield manager
    await manager.close()


@pytest_asyncio.fixture
async def repository(db_manager):
    """Create a PortfolioRepository with initialized database."""
    return PortfolioRepository(db_manager)


# Model Tests


class TestPortfolioModel:
    """Tests for Portfolio dataclass."""

    def test_portfolio_creation(self):
        """Test basic portfolio creation."""
        portfolio = Portfolio(
            telegram_user_id=12345,
            name="Test Portfolio",
        )
        assert portfolio.telegram_user_id == 12345
        assert portfolio.name == "Test Portfolio"
        assert portfolio.id is None

    def test_portfolio_default_name(self):
        """Test portfolio has default name."""
        portfolio = Portfolio(telegram_user_id=12345)
        assert portfolio.name == "My Portfolio"

    def test_portfolio_str(self):
        """Test portfolio string representation."""
        portfolio = Portfolio(telegram_user_id=12345, name="Test")
        assert "Test" in str(portfolio)
        assert "12345" in str(portfolio)


class TestHoldingModel:
    """Tests for Holding dataclass."""

    def test_holding_creation(self):
        """Test basic holding creation."""
        holding = Holding(
            portfolio_id=1,
            symbol="AAPL",
            quantity=10,
            avg_cost=150.00,
        )
        assert holding.symbol == "AAPL"
        assert holding.quantity == 10
        assert holding.avg_cost == 150.00

    def test_holding_total_cost(self):
        """Test total cost calculation."""
        holding = Holding(
            portfolio_id=1,
            symbol="AAPL",
            quantity=10,
            avg_cost=150.00,
        )
        assert holding.total_cost == 1500.00

    def test_holding_formatted_quantity_whole(self):
        """Test formatted quantity for whole numbers."""
        holding = Holding(portfolio_id=1, symbol="AAPL", quantity=10, avg_cost=100)
        assert holding.formatted_quantity == "10"

    def test_holding_formatted_quantity_decimal(self):
        """Test formatted quantity for decimals."""
        holding = Holding(portfolio_id=1, symbol="AAPL", quantity=10.5, avg_cost=100)
        assert holding.formatted_quantity == "10.5"

    def test_holding_str(self):
        """Test holding string representation."""
        holding = Holding(portfolio_id=1, symbol="AAPL", quantity=10, avg_cost=100)
        assert "AAPL" in str(holding)


class TestTransactionModel:
    """Tests for Transaction dataclass."""

    def test_transaction_creation(self):
        """Test basic transaction creation."""
        transaction = Transaction(
            holding_id=1,
            transaction_type=TransactionType.BUY,
            quantity=10,
            price=150.00,
        )
        assert transaction.transaction_type == TransactionType.BUY
        assert transaction.quantity == 10
        assert transaction.price == 150.00

    def test_transaction_total_value(self):
        """Test total value calculation."""
        transaction = Transaction(
            holding_id=1,
            transaction_type=TransactionType.BUY,
            quantity=10,
            price=150.00,
        )
        assert transaction.total_value == 1500.00

    def test_transaction_type_emoji_buy(self):
        """Test emoji for buy transaction."""
        transaction = Transaction(
            holding_id=1,
            transaction_type=TransactionType.BUY,
            quantity=10,
            price=100,
        )
        assert transaction.type_emoji == "🟢"

    def test_transaction_type_emoji_sell(self):
        """Test emoji for sell transaction."""
        transaction = Transaction(
            holding_id=1,
            transaction_type=TransactionType.SELL,
            quantity=10,
            price=100,
        )
        assert transaction.type_emoji == "🔴"

    def test_transaction_str(self):
        """Test transaction string representation."""
        transaction = Transaction(
            holding_id=1,
            transaction_type=TransactionType.BUY,
            quantity=10,
            price=150.00,
        )
        assert "BUY" in str(transaction)
        assert "150.00" in str(transaction)


# Database Connection Tests


class TestDatabaseManager:
    """Tests for DatabaseManager."""

    @pytest.mark.asyncio
    async def test_init_tables(self, temp_db_path):
        """Test database table initialization."""
        manager = DatabaseManager(temp_db_path)
        await manager.init_tables()

        # Verify tables exist
        async with manager.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in await cursor.fetchall()}

        assert "portfolios" in tables
        assert "holdings" in tables
        assert "transactions" in tables
        await manager.close()

    @pytest.mark.asyncio
    async def test_connection_context_manager(self, db_manager):
        """Test connection works as context manager."""
        async with db_manager.get_connection() as conn:
            cursor = await conn.execute("SELECT 1")
            result = await cursor.fetchone()
            assert result[0] == 1

    @pytest.mark.asyncio
    async def test_creates_data_directory(self, temp_db_path):
        """Test that data directory is created if needed."""
        # Use a path in a non-existent subdirectory
        nested_path = temp_db_path.parent / "subdir" / "test.db"
        manager = DatabaseManager(nested_path)
        await manager.init_tables()
        assert nested_path.parent.exists()
        await manager.close()
        # Cleanup
        nested_path.unlink(missing_ok=True)
        nested_path.parent.rmdir()


# Repository Tests


class TestPortfolioRepository:
    """Tests for PortfolioRepository."""

    @pytest.mark.asyncio
    async def test_create_portfolio(self, repository):
        """Test creating a new portfolio."""
        portfolio = await repository.create_portfolio(12345, "Test Portfolio")

        assert portfolio.telegram_user_id == 12345
        assert portfolio.name == "Test Portfolio"
        assert portfolio.id is not None

    @pytest.mark.asyncio
    async def test_create_portfolio_duplicate_returns_existing(self, repository):
        """Test creating duplicate portfolio returns existing."""
        portfolio1 = await repository.create_portfolio(12345, "First")
        portfolio2 = await repository.create_portfolio(12345, "Second")

        assert portfolio1.id == portfolio2.id
        assert portfolio2.name == "First"  # Original name kept

    @pytest.mark.asyncio
    async def test_get_portfolio(self, repository):
        """Test getting an existing portfolio."""
        await repository.create_portfolio(12345, "Test")
        portfolio = await repository.get_portfolio(12345)

        assert portfolio is not None
        assert portfolio.telegram_user_id == 12345

    @pytest.mark.asyncio
    async def test_get_portfolio_not_found(self, repository):
        """Test getting non-existent portfolio returns None."""
        portfolio = await repository.get_portfolio(99999)
        assert portfolio is None

    @pytest.mark.asyncio
    async def test_get_or_create_portfolio_creates(self, repository):
        """Test get_or_create creates when missing."""
        portfolio = await repository.get_or_create_portfolio(12345)
        assert portfolio.telegram_user_id == 12345

    @pytest.mark.asyncio
    async def test_get_or_create_portfolio_gets_existing(self, repository):
        """Test get_or_create returns existing."""
        await repository.create_portfolio(12345, "Existing")
        portfolio = await repository.get_or_create_portfolio(12345, "New Name")

        assert portfolio.name == "Existing"


class TestHoldingOperations:
    """Tests for holding CRUD operations."""

    @pytest.mark.asyncio
    async def test_add_holding(self, repository):
        """Test adding a new holding."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(
            portfolio.id, "AAPL", quantity=10, price=150.00
        )

        assert holding.symbol == "AAPL"
        assert holding.quantity == 10
        assert holding.avg_cost == 150.00

    @pytest.mark.asyncio
    async def test_add_holding_updates_existing(self, repository):
        """Test adding to existing holding updates avg cost."""
        portfolio = await repository.create_portfolio(12345)

        # First buy: 10 shares @ $100
        await repository.add_holding(portfolio.id, "AAPL", quantity=10, price=100.00)

        # Second buy: 10 shares @ $200
        holding = await repository.add_holding(
            portfolio.id, "AAPL", quantity=10, price=200.00
        )

        # Should now have 20 shares @ $150 avg
        assert holding.quantity == 20
        assert holding.avg_cost == 150.00

    @pytest.mark.asyncio
    async def test_add_holding_symbol_uppercase(self, repository):
        """Test that symbol is uppercased."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "aapl", 10, 100)
        assert holding.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_holdings(self, repository):
        """Test getting all holdings for portfolio."""
        portfolio = await repository.create_portfolio(12345)
        await repository.add_holding(portfolio.id, "AAPL", 10, 150)
        await repository.add_holding(portfolio.id, "GOOGL", 5, 2800)

        holdings = await repository.get_holdings(portfolio.id)

        assert len(holdings) == 2
        symbols = {h.symbol for h in holdings}
        assert "AAPL" in symbols
        assert "GOOGL" in symbols

    @pytest.mark.asyncio
    async def test_get_holdings_excludes_zero_quantity(self, repository):
        """Test that zero-quantity holdings are excluded."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 150)
        await repository.remove_holding(holding.id)

        holdings = await repository.get_holdings(portfolio.id)
        assert len(holdings) == 0

    @pytest.mark.asyncio
    async def test_get_holding_by_symbol(self, repository):
        """Test getting specific holding by symbol."""
        portfolio = await repository.create_portfolio(12345)
        await repository.add_holding(portfolio.id, "AAPL", 10, 150)

        holding = await repository.get_holding_by_symbol(portfolio.id, "AAPL")

        assert holding is not None
        assert holding.symbol == "AAPL"

    @pytest.mark.asyncio
    async def test_get_holding_by_symbol_not_found(self, repository):
        """Test getting non-existent symbol returns None."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.get_holding_by_symbol(portfolio.id, "AAPL")
        assert holding is None

    @pytest.mark.asyncio
    async def test_update_holding(self, repository):
        """Test updating a holding."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 150)

        updated = await repository.update_holding(holding.id, quantity=5, avg_cost=160)

        assert updated.quantity == 5
        assert updated.avg_cost == 160

    @pytest.mark.asyncio
    async def test_remove_holding(self, repository):
        """Test removing a holding sets quantity to 0."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 150)

        result = await repository.remove_holding(holding.id)

        assert result is True
        # Verify it's removed from active holdings
        holdings = await repository.get_holdings(portfolio.id)
        assert len(holdings) == 0


class TestTransactionOperations:
    """Tests for transaction operations."""

    @pytest.mark.asyncio
    async def test_add_holding_creates_transaction(self, repository):
        """Test that adding a holding creates a BUY transaction."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 150)

        transactions = await repository.get_transactions(holding.id)

        assert len(transactions) == 1
        assert transactions[0].transaction_type == TransactionType.BUY
        assert transactions[0].quantity == 10
        assert transactions[0].price == 150

    @pytest.mark.asyncio
    async def test_multiple_buys_create_transactions(self, repository):
        """Test that multiple buys create multiple transactions."""
        portfolio = await repository.create_portfolio(12345)
        await repository.add_holding(portfolio.id, "AAPL", 10, 100)
        holding = await repository.add_holding(portfolio.id, "AAPL", 5, 200)

        transactions = await repository.get_transactions(holding.id)

        assert len(transactions) == 2

    @pytest.mark.asyncio
    async def test_record_sell_transaction(self, repository):
        """Test recording a sell transaction."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 150)

        transaction = await repository.record_transaction(
            holding.id, TransactionType.SELL, 5, 175
        )

        assert transaction.transaction_type == TransactionType.SELL
        assert transaction.quantity == 5
        assert transaction.price == 175

    @pytest.mark.asyncio
    async def test_get_transactions_ordered_by_date(self, repository):
        """Test transactions are returned most recent first."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 100)
        await repository.record_transaction(holding.id, TransactionType.SELL, 5, 150)

        transactions = await repository.get_transactions(holding.id)

        # Should have 2 transactions total (BUY from add_holding + SELL)
        assert len(transactions) == 2
        # Verify both transaction types are present
        types = {t.transaction_type for t in transactions}
        assert TransactionType.BUY in types
        assert TransactionType.SELL in types

    @pytest.mark.asyncio
    async def test_get_all_transactions(self, repository):
        """Test getting all transactions with symbols."""
        portfolio = await repository.create_portfolio(12345)
        await repository.add_holding(portfolio.id, "AAPL", 10, 150)
        await repository.add_holding(portfolio.id, "GOOGL", 5, 2800)

        transactions = await repository.get_all_transactions(portfolio.id)

        assert len(transactions) == 2
        symbols = {t[1] for t in transactions}
        assert "AAPL" in symbols
        assert "GOOGL" in symbols

    @pytest.mark.asyncio
    async def test_get_transactions_limit(self, repository):
        """Test transaction limit works."""
        portfolio = await repository.create_portfolio(12345)
        holding = await repository.add_holding(portfolio.id, "AAPL", 10, 100)
        for i in range(5):
            await repository.record_transaction(
                holding.id, TransactionType.SELL, 1, 100 + i
            )

        transactions = await repository.get_transactions(holding.id, limit=3)
        assert len(transactions) == 3


# Integration Tests


class TestDatabaseIntegration:
    """Integration tests for database workflow."""

    @pytest.mark.asyncio
    async def test_full_portfolio_workflow(self, repository):
        """Test complete portfolio workflow."""
        # 1. Create portfolio
        portfolio = await repository.create_portfolio(12345, "My Stocks")
        assert portfolio.id is not None

        # 2. Add holdings
        aapl = await repository.add_holding(portfolio.id, "AAPL", 10, 150)
        await repository.add_holding(portfolio.id, "GOOGL", 5, 2800)

        # 3. Verify holdings
        holdings = await repository.get_holdings(portfolio.id)
        assert len(holdings) == 2

        # 4. Add more AAPL
        aapl = await repository.add_holding(portfolio.id, "AAPL", 10, 170)
        assert aapl.quantity == 20
        assert aapl.avg_cost == 160  # (10*150 + 10*170) / 20

        # 5. Sell some AAPL
        await repository.record_transaction(aapl.id, TransactionType.SELL, 5, 180)

        # 6. Check transactions
        transactions = await repository.get_all_transactions(portfolio.id)
        assert len(transactions) == 4  # 2 AAPL buys + 1 GOOGL buy + 1 AAPL sell

    @pytest.mark.asyncio
    async def test_multiple_users(self, repository):
        """Test multiple users can have separate portfolios."""
        portfolio1 = await repository.create_portfolio(111, "User 1")
        portfolio2 = await repository.create_portfolio(222, "User 2")

        await repository.add_holding(portfolio1.id, "AAPL", 10, 150)
        await repository.add_holding(portfolio2.id, "AAPL", 5, 160)

        holdings1 = await repository.get_holdings(portfolio1.id)
        holdings2 = await repository.get_holdings(portfolio2.id)

        assert holdings1[0].quantity == 10
        assert holdings2[0].quantity == 5
