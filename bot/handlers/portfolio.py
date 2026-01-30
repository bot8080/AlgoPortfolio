"""Portfolio command handler - View holdings with P&L calculations."""

from telegram import Update
from telegram.ext import ContextTypes
from typing import List, Tuple

from models.portfolio import Holding
from services.market_data.yfinance_provider import YFinanceProvider
from services.database.portfolio_repo import PortfolioRepository
from utils.exceptions import SymbolNotFoundError, DataFetchError
from utils.logger import get_logger

logger = get_logger(__name__)


def format_pnl(value: float, percentage: float) -> str:
    """Format P&L with color emoji.

    Args:
        value: Dollar P&L value
        percentage: Percentage P&L

    Returns:
        Formatted string with emoji
    """
    emoji = "🟢" if value >= 0 else "🔴"
    sign = "+" if value >= 0 else ""
    return f"{sign}${value:,.2f} ({sign}{percentage:.2f}%) {emoji}"


def format_quantity(quantity: float) -> str:
    """Format quantity, showing decimals only if needed."""
    if quantity == int(quantity):
        return str(int(quantity))
    return f"{quantity:.4f}".rstrip("0").rstrip(".")


async def fetch_current_prices(
    holdings: List[Holding], provider: YFinanceProvider
) -> List[Tuple[Holding, float]]:
    """Fetch current prices for all holdings.

    Args:
        holdings: List of holdings
        provider: Market data provider

    Returns:
        List of (holding, current_price) tuples
    """
    results = []
    for holding in holdings:
        try:
            price_data = await provider.get_price(holding.symbol)
            results.append((holding, price_data.price))
        except (SymbolNotFoundError, DataFetchError) as e:
            logger.warning(f"Could not fetch price for {holding.symbol}: {e}")
            # Use avg_cost as fallback (shows 0% P&L)
            results.append((holding, holding.avg_cost))
    return results


def format_portfolio_message(
    holdings_with_prices: List[Tuple[Holding, float]],
    portfolio_name: str = "My Portfolio",
) -> str:
    """Format portfolio as Telegram message.

    Args:
        holdings_with_prices: List of (holding, current_price) tuples
        portfolio_name: Name of the portfolio

    Returns:
        Formatted HTML message
    """
    lines = [f"📊 <b>{portfolio_name}</b>\n"]

    total_value = 0.0
    total_cost = 0.0

    for holding, current_price in holdings_with_prices:
        current_value = holding.quantity * current_price
        cost_basis = holding.total_cost
        pnl_value = current_value - cost_basis
        pnl_percent = (pnl_value / cost_basis * 100) if cost_basis > 0 else 0

        total_value += current_value
        total_cost += cost_basis

        qty_str = format_quantity(holding.quantity)
        pnl_str = format_pnl(pnl_value, pnl_percent)

        lines.append(
            f"<b>{holding.symbol}</b> ({qty_str} shares)\n"
            f"├ Avg Cost: ${holding.avg_cost:,.2f}\n"
            f"├ Invested: ${cost_basis:,.2f}\n"
            f"├ Current: ${current_price:,.2f} → ${current_value:,.2f}\n"
            f"└ P&L: {pnl_str}\n"
        )

    # Add total summary
    total_pnl_value = total_value - total_cost
    total_pnl_percent = (total_pnl_value / total_cost * 100) if total_cost > 0 else 0

    lines.append("─" * 28)
    lines.append(f"💰 <b>Total Invested:</b> ${total_cost:,.2f}")
    lines.append(f"📈 <b>Current Value:</b> ${total_value:,.2f}")
    lines.append(f"💵 <b>Total P&L:</b> {format_pnl(total_pnl_value, total_pnl_percent)}")

    return "\n".join(lines)


async def portfolio_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /portfolio command - View holdings with P&L.

    Args:
        update: Telegram update object
        context: Bot context with bot_data containing repository and provider
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested portfolio view")

    # Get dependencies from bot_data
    repo: PortfolioRepository = context.bot_data.get("portfolio_repo")
    provider: YFinanceProvider = context.bot_data.get("market_provider")

    if not repo or not provider:
        logger.error("Portfolio repository or market provider not initialized")
        await update.message.reply_text(
            "Database not initialized. Please contact support.",
            parse_mode="HTML",
        )
        return

    # Send loading message
    status_msg = await update.message.reply_text(
        "Loading portfolio...",
        parse_mode="HTML",
    )

    try:
        # Get or create portfolio for user
        portfolio = await repo.get_or_create_portfolio(user_id)

        # Get holdings
        holdings = await repo.get_holdings(portfolio.id)

        if not holdings:
            await status_msg.edit_text(
                "Your portfolio is empty!\n\n"
                "<b>Get started:</b>\n"
                "<code>/add SYMBOL QTY PRICE</code>\n\n"
                "<i>Example: /add AAPL 10 150.50</i>",
                parse_mode="HTML",
            )
            return

        # Fetch current prices
        holdings_with_prices = await fetch_current_prices(holdings, provider)

        # Format and send message
        message = format_portfolio_message(holdings_with_prices, portfolio.name)
        await status_msg.edit_text(message, parse_mode="HTML")

        logger.info(f"Portfolio displayed for user {user_id}: {len(holdings)} holdings")

    except Exception as e:
        logger.exception(f"Error loading portfolio for user {user_id}: {e}")
        await status_msg.edit_text(
            "An error occurred while loading your portfolio.\n"
            "Please try again later.",
            parse_mode="HTML",
        )
