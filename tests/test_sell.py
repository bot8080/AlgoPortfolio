"""Tests for /sell command handler."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.sell import sell_command


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
    service.sell_holding = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_sell_no_arguments(mock_update, mock_context):
    """Test /sell with no arguments shows usage."""
    mock_context.args = []

    await sell_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid usage" in response
    assert "/sell SYMBOL QTY PRICE" in response


@pytest.mark.asyncio
async def test_sell_missing_price(mock_update, mock_context):
    """Test /sell with missing price shows usage."""
    mock_context.args = ["AAPL", "10"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid usage" in response


@pytest.mark.asyncio
async def test_sell_invalid_symbol(mock_update, mock_context):
    """Test /sell with invalid symbol shows error."""
    mock_context.args = ["AAPL123", "10", "175.00"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid stock symbol" in response


@pytest.mark.asyncio
async def test_sell_invalid_quantity(mock_update, mock_context):
    """Test /sell with invalid quantity shows error."""
    mock_context.args = ["AAPL", "abc", "175.00"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid quantity" in response


@pytest.mark.asyncio
async def test_sell_negative_quantity(mock_update, mock_context):
    """Test /sell with negative quantity shows error."""
    mock_context.args = ["AAPL", "-5", "175.00"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid quantity" in response


@pytest.mark.asyncio
async def test_sell_zero_quantity(mock_update, mock_context):
    """Test /sell with zero quantity shows error."""
    mock_context.args = ["AAPL", "0", "175.00"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid quantity" in response


@pytest.mark.asyncio
async def test_sell_invalid_price(mock_update, mock_context):
    """Test /sell with invalid price shows error."""
    mock_context.args = ["AAPL", "5", "abc"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid price" in response


@pytest.mark.asyncio
async def test_sell_negative_price(mock_update, mock_context):
    """Test /sell with negative price shows error."""
    mock_context.args = ["AAPL", "5", "-175"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid price" in response


@pytest.mark.asyncio
async def test_sell_zero_price(mock_update, mock_context):
    """Test /sell with zero price shows error."""
    mock_context.args = ["AAPL", "5", "0"]

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid price" in response


@pytest.mark.asyncio
async def test_sell_service_not_initialized(mock_update, mock_context):
    """Test /sell when service not available."""
    mock_context.args = ["AAPL", "5", "175.00"]
    mock_context.bot_data = {}

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Service temporarily unavailable" in response


@pytest.mark.asyncio
async def test_sell_stock_not_owned(mock_update, mock_context, mock_portfolio_service):
    """Test /sell when user doesn't own the stock."""
    mock_context.args = ["AAPL", "5", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.sell_holding.return_value = None

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "don't own any AAPL" in response
    assert "/portfolio" in response


@pytest.mark.asyncio
async def test_sell_more_than_owned(mock_update, mock_context, mock_portfolio_service):
    """Test /sell when trying to sell more shares than owned."""
    mock_context.args = ["AAPL", "100", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.sell_holding.side_effect = ValueError(
        "Cannot sell 100 shares. You only own 10."
    )

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Cannot sell 100 shares" in response
    assert "only own 10" in response


@pytest.mark.asyncio
async def test_sell_partial_success(mock_update, mock_context, mock_portfolio_service):
    """Test successful partial sell (some shares remaining)."""
    mock_context.args = ["AAPL", "5", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.symbol = "AAPL"
    mock_holding.quantity = 15  # 15 remaining after selling 5
    mock_holding.avg_cost = 150.50
    mock_portfolio_service.sell_holding.return_value = mock_holding

    await sell_command(mock_update, mock_context)

    # Verify service was called correctly
    mock_portfolio_service.sell_holding.assert_called_once()
    call_kwargs = mock_portfolio_service.sell_holding.call_args[1]
    assert call_kwargs["user_id"] == 12345
    assert call_kwargs["symbol"] == "AAPL"
    assert call_kwargs["quantity"] == Decimal("5")
    assert call_kwargs["sell_price"] == Decimal("175.00")

    # Verify success response
    response = mock_update.message.reply_text.call_args[0][0]
    assert "Sold from portfolio" in response
    assert "AAPL" in response
    assert "175.00" in response
    assert "Remaining: 15" in response


@pytest.mark.asyncio
async def test_sell_full_liquidation(mock_update, mock_context, mock_portfolio_service):
    """Test successful full liquidation (position closed)."""
    mock_context.args = ["AAPL", "20", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.symbol = "AAPL"
    mock_holding.quantity = 0  # All shares sold
    mock_holding.avg_cost = 150.50
    mock_portfolio_service.sell_holding.return_value = mock_holding

    await sell_command(mock_update, mock_context)

    # Verify success response
    response = mock_update.message.reply_text.call_args[0][0]
    assert "Position closed" in response
    assert "AAPL" in response
    assert "175.00" in response
    assert "fully liquidated" in response


@pytest.mark.asyncio
async def test_sell_lowercase_symbol_converted(mock_update, mock_context, mock_portfolio_service):
    """Test that lowercase symbols are converted to uppercase."""
    mock_context.args = ["aapl", "5", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.quantity = 10
    mock_portfolio_service.sell_holding.return_value = mock_holding

    await sell_command(mock_update, mock_context)

    call_kwargs = mock_portfolio_service.sell_holding.call_args[1]
    assert call_kwargs["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_sell_decimal_quantity(mock_update, mock_context, mock_portfolio_service):
    """Test /sell with decimal quantity (fractional shares)."""
    mock_context.args = ["AAPL", "5.5", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.quantity = 10
    mock_portfolio_service.sell_holding.return_value = mock_holding

    await sell_command(mock_update, mock_context)

    call_kwargs = mock_portfolio_service.sell_holding.call_args[1]
    assert call_kwargs["quantity"] == Decimal("5.5")


@pytest.mark.asyncio
async def test_sell_service_error(mock_update, mock_context, mock_portfolio_service):
    """Test /sell when service raises unexpected error."""
    mock_context.args = ["AAPL", "5", "175.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.sell_holding.side_effect = Exception("Database error")

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Failed to sell stock" in response


@pytest.mark.asyncio
async def test_sell_calculates_proceeds_correctly(
    mock_update, mock_context, mock_portfolio_service
):
    """Test that total proceeds are calculated correctly."""
    mock_context.args = ["AAPL", "10", "200.00"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.quantity = 5
    mock_portfolio_service.sell_holding.return_value = mock_holding

    await sell_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    # 10 * 200 = 2000
    assert "2000.00" in response
