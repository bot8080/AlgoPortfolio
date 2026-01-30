"""Tests for portfolio command handler."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.portfolio import (
    portfolio_command,
    format_portfolio_message,
    format_pnl,
    format_quantity,
    fetch_current_prices,
)
from models.portfolio import Portfolio, Holding
from models.stock import StockPrice
from utils.exceptions import SymbolNotFoundError


class TestFormatPnl:
    """Tests for format_pnl helper function."""

    def test_positive_pnl_shows_green(self):
        """Test positive P&L shows green emoji and plus sign."""
        result = format_pnl(100.0, 5.0)
        assert "🟢" in result
        assert "+$100.00" in result
        assert "+5.00%" in result

    def test_negative_pnl_shows_red(self):
        """Test negative P&L shows red emoji without plus sign."""
        result = format_pnl(-50.0, -2.5)
        assert "🔴" in result
        assert "$-50.00" in result  # Python's format puts sign after $
        assert "-2.50%" in result

    def test_zero_pnl_shows_green(self):
        """Test zero P&L shows green emoji."""
        result = format_pnl(0.0, 0.0)
        assert "🟢" in result
        assert "+$0.00" in result


class TestFormatQuantity:
    """Tests for format_quantity helper function."""

    def test_whole_number_no_decimals(self):
        """Test whole numbers display without decimals."""
        assert format_quantity(10.0) == "10"
        assert format_quantity(100.0) == "100"

    def test_decimal_shows_decimals(self):
        """Test fractional shares show decimals."""
        assert format_quantity(10.5) == "10.5"
        assert format_quantity(10.1234) == "10.1234"

    def test_trailing_zeros_stripped(self):
        """Test trailing zeros are stripped."""
        assert format_quantity(10.5000) == "10.5"


class TestFetchCurrentPrices:
    """Tests for fetch_current_prices function."""

    @pytest.fixture
    def sample_holdings(self):
        """Create sample holdings for testing."""
        return [
            Holding(
                id=1,
                portfolio_id=1,
                symbol="AAPL",
                quantity=10,
                avg_cost=150.0,
                created_at=datetime.now(),
            ),
            Holding(
                id=2,
                portfolio_id=1,
                symbol="GOOGL",
                quantity=5,
                avg_cost=2800.0,
                created_at=datetime.now(),
            ),
        ]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_fetches_prices_for_all_holdings(self, sample_holdings):
        """Test prices are fetched for all holdings."""
        mock_provider = MagicMock()
        mock_provider.get_price = AsyncMock(
            side_effect=[
                StockPrice(
                    symbol="AAPL",
                    price=175.0,
                    change=2.0,
                    change_percent=1.15,
                    volume=50_000_000,
                    timestamp=datetime.now(),
                    currency="USD",
                ),
                StockPrice(
                    symbol="GOOGL",
                    price=2900.0,
                    change=50.0,
                    change_percent=1.75,
                    volume=10_000_000,
                    timestamp=datetime.now(),
                    currency="USD",
                ),
            ]
        )

        results = await fetch_current_prices(sample_holdings, mock_provider)

        assert len(results) == 2
        assert results[0][0].symbol == "AAPL"
        assert results[0][1] == 175.0
        assert results[1][0].symbol == "GOOGL"
        assert results[1][1] == 2900.0

    @pytest.mark.asyncio(loop_scope="function")
    async def test_uses_avg_cost_on_error(self, sample_holdings):
        """Test avg_cost is used as fallback when price fetch fails."""
        mock_provider = MagicMock()
        mock_provider.get_price = AsyncMock(
            side_effect=[
                SymbolNotFoundError("AAPL"),
                StockPrice(
                    symbol="GOOGL",
                    price=2900.0,
                    change=50.0,
                    change_percent=1.75,
                    volume=10_000_000,
                    timestamp=datetime.now(),
                    currency="USD",
                ),
            ]
        )

        results = await fetch_current_prices(sample_holdings, mock_provider)

        # First holding should use avg_cost as fallback
        assert results[0][1] == 150.0  # avg_cost
        assert results[1][1] == 2900.0  # actual price


class TestFormatPortfolioMessage:
    """Tests for format_portfolio_message function."""

    @pytest.fixture
    def sample_holdings_with_prices(self):
        """Create sample holdings with prices for testing."""
        holdings = [
            Holding(
                id=1,
                portfolio_id=1,
                symbol="AAPL",
                quantity=10,
                avg_cost=150.0,
                created_at=datetime.now(),
            ),
            Holding(
                id=2,
                portfolio_id=1,
                symbol="GOOGL",
                quantity=5,
                avg_cost=2800.0,
                created_at=datetime.now(),
            ),
        ]
        # AAPL: 10 shares @ $150 = $1500 cost, now $175 = $1750 value, +$250 P&L
        # GOOGL: 5 shares @ $2800 = $14000 cost, now $2650 = $13250 value, -$750 P&L
        return [(holdings[0], 175.0), (holdings[1], 2650.0)]

    def test_includes_portfolio_name(self, sample_holdings_with_prices):
        """Test message includes portfolio name."""
        message = format_portfolio_message(sample_holdings_with_prices, "Test Portfolio")
        assert "Test Portfolio" in message

    def test_includes_symbols(self, sample_holdings_with_prices):
        """Test message includes all stock symbols."""
        message = format_portfolio_message(sample_holdings_with_prices)
        assert "AAPL" in message
        assert "GOOGL" in message

    def test_includes_quantities(self, sample_holdings_with_prices):
        """Test message includes share quantities."""
        message = format_portfolio_message(sample_holdings_with_prices)
        assert "10 shares" in message
        assert "5 shares" in message

    def test_includes_avg_cost(self, sample_holdings_with_prices):
        """Test message includes average cost."""
        message = format_portfolio_message(sample_holdings_with_prices)
        assert "$150.00" in message
        assert "$2,800.00" in message

    def test_includes_current_prices(self, sample_holdings_with_prices):
        """Test message includes current prices."""
        message = format_portfolio_message(sample_holdings_with_prices)
        assert "$175.00" in message
        assert "$2,650.00" in message

    def test_shows_positive_pnl_green(self, sample_holdings_with_prices):
        """Test positive P&L shows green emoji."""
        message = format_portfolio_message(sample_holdings_with_prices)
        # AAPL has positive P&L
        assert "🟢" in message

    def test_shows_negative_pnl_red(self, sample_holdings_with_prices):
        """Test negative P&L shows red emoji."""
        message = format_portfolio_message(sample_holdings_with_prices)
        # GOOGL has negative P&L
        assert "🔴" in message

    def test_includes_total_value(self, sample_holdings_with_prices):
        """Test message includes total portfolio value."""
        message = format_portfolio_message(sample_holdings_with_prices)
        # AAPL: $1750 + GOOGL: $13250 = $15000
        assert "Current Value" in message
        assert "$15,000.00" in message

    def test_includes_total_pnl(self, sample_holdings_with_prices):
        """Test message includes total P&L."""
        message = format_portfolio_message(sample_holdings_with_prices)
        # +$250 - $750 = -$500
        assert "Total P&L" in message


class TestPortfolioCommand:
    """Tests for /portfolio command handler."""

    @pytest.fixture
    def mock_update(self):
        """Create a mock Telegram Update object."""
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock Telegram Context object."""
        context = MagicMock()
        context.bot_data = {}
        return context

    @pytest.fixture
    def mock_status_message(self):
        """Create a mock status message that can be edited."""
        msg = MagicMock()
        msg.edit_text = AsyncMock()
        return msg

    @pytest.fixture
    def mock_repo(self):
        """Create a mock PortfolioRepository."""
        repo = MagicMock()
        repo.get_or_create_portfolio = AsyncMock()
        repo.get_holdings = AsyncMock()
        return repo

    @pytest.fixture
    def mock_provider(self):
        """Create a mock YFinanceProvider."""
        provider = MagicMock()
        provider.get_price = AsyncMock()
        return provider

    @pytest.mark.asyncio(loop_scope="function")
    async def test_no_dependencies_shows_error(
        self, mock_update, mock_context, mock_status_message
    ):
        """Test command shows error when dependencies not initialized."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        await portfolio_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]
        assert "not initialized" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_empty_portfolio_shows_help(
        self, mock_update, mock_context, mock_status_message, mock_repo, mock_provider
    ):
        """Test empty portfolio shows help message."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)
        mock_context.bot_data["portfolio_repo"] = mock_repo
        mock_context.bot_data["market_provider"] = mock_provider

        mock_repo.get_or_create_portfolio.return_value = Portfolio(
            id=1, telegram_user_id=123456789, name="My Portfolio"
        )
        mock_repo.get_holdings.return_value = []

        await portfolio_command(mock_update, mock_context)

        mock_status_message.edit_text.assert_called_once()
        message = mock_status_message.edit_text.call_args[0][0]
        assert "empty" in message
        assert "/add" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_shows_loading_message(
        self, mock_update, mock_context, mock_status_message, mock_repo, mock_provider
    ):
        """Test command shows loading message first."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)
        mock_context.bot_data["portfolio_repo"] = mock_repo
        mock_context.bot_data["market_provider"] = mock_provider

        mock_repo.get_or_create_portfolio.return_value = Portfolio(
            id=1, telegram_user_id=123456789, name="My Portfolio"
        )
        mock_repo.get_holdings.return_value = []

        await portfolio_command(mock_update, mock_context)

        # First call should be loading message
        first_call = mock_update.message.reply_text.call_args
        message = first_call[0][0]
        assert "Loading" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_shows_portfolio_with_holdings(
        self, mock_update, mock_context, mock_status_message, mock_repo, mock_provider
    ):
        """Test command shows portfolio when holdings exist."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)
        mock_context.bot_data["portfolio_repo"] = mock_repo
        mock_context.bot_data["market_provider"] = mock_provider

        mock_repo.get_or_create_portfolio.return_value = Portfolio(
            id=1, telegram_user_id=123456789, name="My Portfolio"
        )
        mock_repo.get_holdings.return_value = [
            Holding(
                id=1,
                portfolio_id=1,
                symbol="AAPL",
                quantity=10,
                avg_cost=150.0,
                created_at=datetime.now(),
            )
        ]
        mock_provider.get_price.return_value = StockPrice(
            symbol="AAPL",
            price=175.0,
            change=2.0,
            change_percent=1.15,
            volume=50_000_000,
            timestamp=datetime.now(),
            currency="USD",
        )

        await portfolio_command(mock_update, mock_context)

        # Final message should contain portfolio info
        final_call = mock_status_message.edit_text.call_args
        message = final_call[0][0]
        assert "AAPL" in message
        assert "10 shares" in message
        assert "$175.00" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_uses_html_parse_mode(
        self, mock_update, mock_context, mock_status_message, mock_repo, mock_provider
    ):
        """Test command uses HTML parse mode."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)
        mock_context.bot_data["portfolio_repo"] = mock_repo
        mock_context.bot_data["market_provider"] = mock_provider

        mock_repo.get_or_create_portfolio.return_value = Portfolio(
            id=1, telegram_user_id=123456789, name="My Portfolio"
        )
        mock_repo.get_holdings.return_value = []

        await portfolio_command(mock_update, mock_context)

        call_kwargs = mock_status_message.edit_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio(loop_scope="function")
    async def test_handles_database_error(
        self, mock_update, mock_context, mock_status_message, mock_repo, mock_provider
    ):
        """Test command handles database errors gracefully."""
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)
        mock_context.bot_data["portfolio_repo"] = mock_repo
        mock_context.bot_data["market_provider"] = mock_provider

        mock_repo.get_or_create_portfolio.side_effect = Exception("Database error")

        await portfolio_command(mock_update, mock_context)

        mock_status_message.edit_text.assert_called_once()
        message = mock_status_message.edit_text.call_args[0][0]
        assert "error" in message.lower()
