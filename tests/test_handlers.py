"""Tests for Telegram bot handlers."""

import pytest
from unittest.mock import AsyncMock, patch

from bot.handlers.start import start_command, help_command
from bot.handlers.analysis import analyze_command, format_analysis_message
from utils.exceptions import SymbolNotFoundError, DataFetchError


class TestStartCommand:
    """Tests for /start command handler."""

    @pytest.mark.asyncio(loop_scope="function")
    async def test_start_command_sends_welcome(self, mock_update, mock_context):
        """Test /start sends welcome message with user's name."""
        await start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0]

        # Check message contains key elements
        assert "Welcome" in message
        assert mock_update.effective_user.first_name in message
        assert "AlgoPortfolio" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_start_command_uses_html_parse_mode(self, mock_update, mock_context):
        """Test /start uses HTML parse mode."""
        await start_command(mock_update, mock_context)

        call_kwargs = mock_update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio(loop_scope="function")
    async def test_start_command_mentions_analyze(self, mock_update, mock_context):
        """Test /start mentions the /analyze command."""
        await start_command(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "/analyze" in message


class TestHelpCommand:
    """Tests for /help command handler."""

    @pytest.mark.asyncio(loop_scope="function")
    async def test_help_command_sends_help(self, mock_update, mock_context):
        """Test /help sends help message."""
        await help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]

        assert "Commands" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_help_command_lists_analyze(self, mock_update, mock_context):
        """Test /help lists the analyze command."""
        await help_command(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "/analyze" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_help_command_uses_html_parse_mode(self, mock_update, mock_context):
        """Test /help uses HTML parse mode."""
        await help_command(mock_update, mock_context)

        call_kwargs = mock_update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"


class TestAnalyzeCommand:
    """Tests for /analyze command handler."""

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_no_symbol_shows_usage(self, mock_update, mock_context):
        """Test /analyze without symbol shows usage message."""
        mock_context.args = []

        await analyze_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]
        assert "Please provide a stock symbol" in message
        assert "/analyze AAPL" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_converts_to_uppercase(
        self, mock_update, mock_context, mock_status_message, sample_stock_price, sample_stock_info
    ):
        """Test /analyze converts symbol to uppercase."""
        mock_context.args = ["aapl"]
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        with patch("bot.handlers.analysis.provider") as mock_provider:
            mock_provider.get_price = AsyncMock(return_value=sample_stock_price)
            mock_provider.get_info = AsyncMock(return_value=sample_stock_info)

            await analyze_command(mock_update, mock_context)

            # Verify uppercase symbol was used
            mock_provider.get_price.assert_called_with("AAPL")
            mock_provider.get_info.assert_called_with("AAPL")

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_shows_analyzing_message(
        self, mock_update, mock_context, mock_status_message, sample_stock_price, sample_stock_info
    ):
        """Test /analyze shows 'Analyzing...' status first."""
        mock_context.args = ["AAPL"]
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        with patch("bot.handlers.analysis.provider") as mock_provider:
            mock_provider.get_price = AsyncMock(return_value=sample_stock_price)
            mock_provider.get_info = AsyncMock(return_value=sample_stock_info)

            await analyze_command(mock_update, mock_context)

            # First call should be the "Analyzing..." message
            first_call = mock_update.message.reply_text.call_args
            message = first_call[0][0]
            assert "Analyzing" in message
            assert "AAPL" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_handles_invalid_symbol(
        self, mock_update, mock_context, mock_status_message
    ):
        """Test /analyze handles invalid symbol gracefully."""
        mock_context.args = ["INVALIDXYZ"]
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        with patch("bot.handlers.analysis.provider") as mock_provider:
            mock_provider.get_price = AsyncMock(
                side_effect=SymbolNotFoundError("INVALIDXYZ")
            )

            await analyze_command(mock_update, mock_context)

            # Should edit the status message with error
            mock_status_message.edit_text.assert_called_once()
            message = mock_status_message.edit_text.call_args[0][0]
            assert "Symbol not found" in message
            assert "INVALIDXYZ" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_handles_data_fetch_error(
        self, mock_update, mock_context, mock_status_message
    ):
        """Test /analyze handles data fetch errors gracefully."""
        mock_context.args = ["AAPL"]
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        with patch("bot.handlers.analysis.provider") as mock_provider:
            mock_provider.get_price = AsyncMock(
                side_effect=DataFetchError("Network timeout")
            )

            await analyze_command(mock_update, mock_context)

            mock_status_message.edit_text.assert_called_once()
            message = mock_status_message.edit_text.call_args[0][0]
            assert "Error" in message

    @pytest.mark.asyncio(loop_scope="function")
    async def test_analyze_success_shows_price(
        self, mock_update, mock_context, mock_status_message, sample_stock_price, sample_stock_info
    ):
        """Test successful /analyze shows stock price."""
        mock_context.args = ["AAPL"]
        mock_update.message.reply_text = AsyncMock(return_value=mock_status_message)

        with patch("bot.handlers.analysis.provider") as mock_provider:
            mock_provider.get_price = AsyncMock(return_value=sample_stock_price)
            mock_provider.get_info = AsyncMock(return_value=sample_stock_info)

            await analyze_command(mock_update, mock_context)

            # Final message should contain price info
            final_call = mock_status_message.edit_text.call_args
            message = final_call[0][0]
            assert "150.25" in message or "$150" in message


class TestFormatAnalysisMessage:
    """Tests for format_analysis_message function."""

    def test_format_includes_symbol(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes stock symbol."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "AAPL" in message

    def test_format_includes_company_name(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes company name."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "Apple Inc." in message

    def test_format_includes_price(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes current price."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "$150.25" in message

    def test_format_positive_shows_green(self, sample_stock_price, sample_stock_info):
        """Test positive change shows green indicator and up emoji."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        # Check for green emoji (positive indicator)
        assert "🟢" in message

    def test_format_negative_shows_red(self, sample_stock_price_negative, sample_stock_info):
        """Test negative change shows red indicator and down emoji."""
        # Update sample_stock_info symbol to match
        sample_stock_info.symbol = "TSLA"
        sample_stock_info.name = "Tesla, Inc."

        message = format_analysis_message(sample_stock_price_negative, sample_stock_info)
        # Check for red emoji (negative indicator)
        assert "🔴" in message

    def test_format_includes_market_cap(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes market cap."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "Market Cap" in message
        assert "$2.50T" in message

    def test_format_includes_pe_ratio(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes P/E ratio."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "P/E" in message
        assert "28.50" in message

    def test_format_handles_missing_pe(self, sample_stock_price, sample_stock_info_minimal):
        """Test format handles missing P/E ratio (ETFs)."""
        sample_stock_price.symbol = "SPY"
        message = format_analysis_message(sample_stock_price, sample_stock_info_minimal)
        assert "N/A" in message

    def test_format_includes_sector(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes sector."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "Sector" in message
        assert "Technology" in message

    def test_format_includes_52_week_range(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes 52-week range."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "52W Range" in message
        assert "$124.17" in message
        assert "$199.62" in message

    def test_format_includes_timestamp(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes data timestamp."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "2024-01-15" in message

    def test_format_includes_source(self, sample_stock_price, sample_stock_info):
        """Test formatted message includes data source."""
        message = format_analysis_message(sample_stock_price, sample_stock_info)
        assert "YFinance" in message
