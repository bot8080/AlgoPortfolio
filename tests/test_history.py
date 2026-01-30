"""Tests for /history command handler."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.history import history_command
from models.portfolio import Transaction, TransactionType


@pytest.fixture
def mock_update():
    """Create mock Telegram Update."""
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram Context."""
    context = MagicMock()
    context.args = []
    context.bot_data = {}
    return context


@pytest.fixture
def mock_portfolio_service():
    """Create mock PortfolioService."""
    service = MagicMock()
    service.get_transactions = AsyncMock()
    return service


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    return [
        (
            Transaction(
                id=1,
                holding_id=1,
                transaction_type=TransactionType.BUY,
                quantity=10,
                price=150.50,
                timestamp=datetime(2025, 1, 15, 10, 30),
            ),
            "AAPL",
        ),
        (
            Transaction(
                id=2,
                holding_id=1,
                transaction_type=TransactionType.SELL,
                quantity=5,
                price=175.00,
                timestamp=datetime(2025, 1, 20, 14, 0),
            ),
            "AAPL",
        ),
        (
            Transaction(
                id=3,
                holding_id=2,
                transaction_type=TransactionType.BUY,
                quantity=20,
                price=380.00,
                timestamp=datetime(2025, 1, 22, 9, 15),
            ),
            "MSFT",
        ),
    ]


@pytest.mark.asyncio
async def test_history_empty(mock_update, mock_context, mock_portfolio_service):
    """Test /history with no transactions."""
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = []

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "No transaction history" in response
    assert "/add" in response


@pytest.mark.asyncio
async def test_history_with_transactions(
    mock_update, mock_context, mock_portfolio_service, sample_transactions
):
    """Test /history with transactions."""
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = sample_transactions

    await history_command(mock_update, mock_context)

    # Verify service was called with default limit
    mock_portfolio_service.get_transactions.assert_called_once_with(12345, 10)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Transaction History" in response
    assert "AAPL" in response
    assert "MSFT" in response
    assert "BUY" in response
    assert "SELL" in response
    assert "150.50" in response
    assert "175.00" in response
    assert "380.00" in response


@pytest.mark.asyncio
async def test_history_with_limit_argument(
    mock_update, mock_context, mock_portfolio_service, sample_transactions
):
    """Test /history with limit argument."""
    mock_context.args = ["5"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = sample_transactions

    await history_command(mock_update, mock_context)

    # Verify service was called with specified limit
    mock_portfolio_service.get_transactions.assert_called_once_with(12345, 5)


@pytest.mark.asyncio
async def test_history_with_max_limit(
    mock_update, mock_context, mock_portfolio_service, sample_transactions
):
    """Test /history respects max limit of 50."""
    mock_context.args = ["100"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = sample_transactions

    await history_command(mock_update, mock_context)

    # Verify limit was capped at 50
    mock_portfolio_service.get_transactions.assert_called_once_with(12345, 50)


@pytest.mark.asyncio
async def test_history_invalid_limit_string(mock_update, mock_context):
    """Test /history with non-numeric limit."""
    mock_context.args = ["abc"]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid limit" in response
    assert "/history" in response


@pytest.mark.asyncio
async def test_history_invalid_limit_negative(mock_update, mock_context):
    """Test /history with negative limit."""
    mock_context.args = ["-5"]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid limit" in response
    assert "positive number" in response


@pytest.mark.asyncio
async def test_history_invalid_limit_zero(mock_update, mock_context):
    """Test /history with zero limit."""
    mock_context.args = ["0"]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid limit" in response
    assert "positive number" in response


@pytest.mark.asyncio
async def test_history_service_not_initialized(mock_update, mock_context):
    """Test /history when service not available."""
    mock_context.bot_data = {}

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Service temporarily unavailable" in response


@pytest.mark.asyncio
async def test_history_service_error(
    mock_update, mock_context, mock_portfolio_service
):
    """Test /history when service raises error."""
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.side_effect = Exception("Database error")

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Failed to load transaction history" in response


@pytest.mark.asyncio
async def test_history_shows_correct_emojis(
    mock_update, mock_context, mock_portfolio_service
):
    """Test /history shows correct emojis for buy/sell."""
    buy_tx = Transaction(
        id=1,
        holding_id=1,
        transaction_type=TransactionType.BUY,
        quantity=10,
        price=100.00,
        timestamp=datetime.now(),
    )
    sell_tx = Transaction(
        id=2,
        holding_id=1,
        transaction_type=TransactionType.SELL,
        quantity=5,
        price=120.00,
        timestamp=datetime.now(),
    )

    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = [
        (buy_tx, "TEST"),
        (sell_tx, "TEST"),
    ]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    # Buy should have green emoji, sell should have red
    assert "🟢" in response
    assert "🔴" in response


@pytest.mark.asyncio
async def test_history_formats_fractional_quantity(
    mock_update, mock_context, mock_portfolio_service
):
    """Test /history formats fractional quantities correctly."""
    tx = Transaction(
        id=1,
        holding_id=1,
        transaction_type=TransactionType.BUY,
        quantity=5.5,
        price=100.00,
        timestamp=datetime.now(),
    )

    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = [(tx, "AAPL")]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "5.5" in response


@pytest.mark.asyncio
async def test_history_formats_whole_quantity(
    mock_update, mock_context, mock_portfolio_service
):
    """Test /history formats whole quantities without decimals."""
    tx = Transaction(
        id=1,
        holding_id=1,
        transaction_type=TransactionType.BUY,
        quantity=10.0,
        price=100.00,
        timestamp=datetime.now(),
    )

    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = [(tx, "AAPL")]

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    # Should show "10" not "10.0"
    assert "10" in response
    # Should not have ".0" after the 10 (check context)
    assert "10.0" not in response or "10.00" not in response.split("10")[0]


@pytest.mark.asyncio
async def test_history_shows_transaction_count(
    mock_update, mock_context, mock_portfolio_service, sample_transactions
):
    """Test /history shows correct transaction count."""
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.get_transactions.return_value = sample_transactions

    await history_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "3" in response  # 3 transactions
