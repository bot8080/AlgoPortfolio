"""History command handler - View transaction history."""

from telegram import Update
from telegram.ext import ContextTypes

from services.database.portfolio_service import PortfolioService
from utils.logger import get_logger

logger = get_logger(__name__)

# Constants
DEFAULT_LIMIT = 10
MAX_LIMIT = 50


def format_quantity(quantity: float) -> str:
    """Format quantity, showing decimals only if needed."""
    if quantity == int(quantity):
        return str(int(quantity))
    return f"{quantity:.4f}".rstrip("0").rstrip(".")


def format_transaction_line(transaction, symbol: str) -> str:
    """Format a single transaction for display.

    Args:
        transaction: Transaction object
        symbol: Stock symbol

    Returns:
        Formatted transaction line
    """
    emoji = transaction.type_emoji
    type_str = transaction.transaction_type.value
    qty_str = format_quantity(transaction.quantity)
    price_str = f"${transaction.price:,.2f}"
    date_str = transaction.timestamp.strftime("%b %d")

    # Pad symbol and type for alignment
    return f"{emoji} {type_str:<4} {symbol:<6} {qty_str:>6} @ {price_str:<10} {date_str}"


async def history_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /history command - View transaction history.

    Usage: /history [limit]

    Args:
        update: Telegram update object
        context: Bot context with bot_data containing portfolio_service
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested transaction history")

    # Parse optional limit argument
    limit = DEFAULT_LIMIT
    if context.args:
        try:
            limit = int(context.args[0])
            if limit <= 0:
                await update.message.reply_text(
                    "Invalid limit. Please provide a positive number.\n\n"
                    "<b>Usage:</b> <code>/history [limit]</code>\n"
                    "<i>Example: /history 20</i>",
                    parse_mode="HTML",
                )
                return
            if limit > MAX_LIMIT:
                limit = MAX_LIMIT
        except ValueError:
            await update.message.reply_text(
                "Invalid limit. Please provide a number.\n\n"
                "<b>Usage:</b> <code>/history [limit]</code>\n"
                "<i>Example: /history 20</i>",
                parse_mode="HTML",
            )
            return

    # Get service from bot_data
    service: PortfolioService = context.bot_data.get("portfolio_service")
    if not service:
        logger.error("Portfolio service not initialized")
        await update.message.reply_text(
            "Service temporarily unavailable. Please try again later.",
            parse_mode="HTML",
        )
        return

    try:
        # Get transactions
        transactions = await service.get_transactions(user_id, limit)

        if not transactions:
            await update.message.reply_text(
                "No transaction history yet.\n\n"
                "<b>Get started:</b>\n"
                "<code>/add SYMBOL QTY PRICE</code> - Add a stock\n\n"
                "<i>Example: /add AAPL 10 150.50</i>",
                parse_mode="HTML",
            )
            return

        # Format transactions
        lines = ["📜 <b>Transaction History</b>\n"]

        for transaction, symbol in transactions:
            lines.append(f"<code>{format_transaction_line(transaction, symbol)}</code>")

        # Add footer
        total_count = len(transactions)
        if total_count == limit:
            lines.append(f"\n<i>Showing {total_count} transactions (limit: {limit})</i>")
        else:
            lines.append(f"\n<i>Showing {total_count} of {total_count} transactions</i>")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")

        logger.info(f"Displayed {total_count} transactions for user {user_id}")

    except Exception as e:
        logger.exception(f"Error fetching history for user {user_id}: {e}")
        await update.message.reply_text(
            "Failed to load transaction history. Please try again later.",
            parse_mode="HTML",
        )
