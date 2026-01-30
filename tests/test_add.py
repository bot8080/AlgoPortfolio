"""Tests for /add command handler."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.add import add_command


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
    service.add_holding = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_add_no_arguments(mock_update, mock_context):
    """Test /add with no arguments shows usage."""
    mock_context.args = []

    await add_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid usage" in response
    assert "/add SYMBOL QTY PRICE" in response


@pytest.mark.asyncio
async def test_add_missing_price(mock_update, mock_context):
    """Test /add with missing price shows usage."""
    mock_context.args = ["AAPL", "10"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid usage" in response


@pytest.mark.asyncio
async def test_add_invalid_symbol(mock_update, mock_context):
    """Test /add with invalid symbol shows error."""
    mock_context.args = ["AAPL123", "10", "150.50"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid stock symbol" in response


@pytest.mark.asyncio
async def test_add_invalid_quantity(mock_update, mock_context):
    """Test /add with invalid quantity shows error."""
    mock_context.args = ["AAPL", "abc", "150.50"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid quantity" in response


@pytest.mark.asyncio
async def test_add_negative_quantity(mock_update, mock_context):
    """Test /add with negative quantity shows error."""
    mock_context.args = ["AAPL", "-10", "150.50"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid quantity" in response


@pytest.mark.asyncio
async def test_add_invalid_price(mock_update, mock_context):
    """Test /add with invalid price shows error."""
    mock_context.args = ["AAPL", "10", "abc"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid price" in response


@pytest.mark.asyncio
async def test_add_negative_price(mock_update, mock_context):
    """Test /add with negative price shows error."""
    mock_context.args = ["AAPL", "10", "-150"]

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid price" in response


@pytest.mark.asyncio
async def test_add_service_not_initialized(mock_update, mock_context):
    """Test /add when service not available."""
    mock_context.args = ["AAPL", "10", "150.50"]
    mock_context.bot_data = {}

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Service temporarily unavailable" in response


@pytest.mark.asyncio
async def test_add_success(mock_update, mock_context, mock_portfolio_service):
    """Test successful /add command."""
    mock_context.args = ["AAPL", "10", "150.50"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_holding.symbol = "AAPL"
    mock_holding.quantity = 10
    mock_holding.avg_cost = 150.50
    mock_portfolio_service.add_holding.return_value = mock_holding

    await add_command(mock_update, mock_context)

    # Verify service was called correctly
    mock_portfolio_service.add_holding.assert_called_once()
    call_kwargs = mock_portfolio_service.add_holding.call_args[1]
    assert call_kwargs["user_id"] == 12345
    assert call_kwargs["symbol"] == "AAPL"
    assert call_kwargs["quantity"] == Decimal("10")
    assert call_kwargs["purchase_price"] == Decimal("150.50")

    # Verify success response
    response = mock_update.message.reply_text.call_args[0][0]
    assert "Added to portfolio" in response
    assert "AAPL" in response
    assert "150.50" in response


@pytest.mark.asyncio
async def test_add_lowercase_symbol_converted(mock_update, mock_context, mock_portfolio_service):
    """Test that lowercase symbols are converted to uppercase."""
    mock_context.args = ["aapl", "10", "150.50"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_portfolio_service.add_holding.return_value = mock_holding

    await add_command(mock_update, mock_context)

    call_kwargs = mock_portfolio_service.add_holding.call_args[1]
    assert call_kwargs["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_add_decimal_quantity(mock_update, mock_context, mock_portfolio_service):
    """Test /add with decimal quantity (fractional shares)."""
    mock_context.args = ["AAPL", "10.5", "150.50"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}

    mock_holding = MagicMock()
    mock_portfolio_service.add_holding.return_value = mock_holding

    await add_command(mock_update, mock_context)

    call_kwargs = mock_portfolio_service.add_holding.call_args[1]
    assert call_kwargs["quantity"] == Decimal("10.5")


@pytest.mark.asyncio
async def test_add_service_error(mock_update, mock_context, mock_portfolio_service):
    """Test /add when service raises error."""
    mock_context.args = ["AAPL", "10", "150.50"]
    mock_context.bot_data = {"portfolio_service": mock_portfolio_service}
    mock_portfolio_service.add_holding.side_effect = Exception("Database error")

    await add_command(mock_update, mock_context)

    response = mock_update.message.reply_text.call_args[0][0]
    assert "Failed to add stock" in response
