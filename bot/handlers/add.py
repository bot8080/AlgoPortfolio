"""
Handler for /add command.
Add stock to your portfolio.
"""
from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.ext import ContextTypes

from services.database import PortfolioService
from utils.logger import get_logger

logger = get_logger(__name__)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add command - Add stock to your portfolio.

    Usage: /add SYMBOL QUANTITY PRICE
    Example: /add AAPL 10 150.50
    """
    user = update.effective_user
    logger.info(f"User {user.id} used /add")

    # Check arguments
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Invalid usage.\n\n"
            "Usage: /add SYMBOL QTY PRICE\n"
            "Example: /add AAPL 10 150.50"
        )
        return

    # Parse arguments
    symbol = context.args[0].upper().strip()
    quantity_str = context.args[1]
    price_str = context.args[2]

    # Validate symbol
    if not symbol.isalpha() or len(symbol) > 10:
        await update.message.reply_text(
            "❌ Invalid stock symbol.\n\n"
            "Symbol should be letters only (e.g., AAPL, MSFT, GOOGL)"
        )
        return

    # Validate and parse quantity
    try:
        quantity = Decimal(quantity_str)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except (InvalidOperation, ValueError):
        await update.message.reply_text(
            "❌ Invalid quantity.\n\n"
            "Quantity must be a positive number.\n"
            "Example: /add AAPL 10 150.50"
        )
        return

    # Validate and parse price
    try:
        price = Decimal(price_str)
        if price <= 0:
            raise ValueError("Price must be positive")
    except (InvalidOperation, ValueError):
        await update.message.reply_text(
            "❌ Invalid price.\n\n"
            "Price must be a positive number.\n"
            "Example: /add AAPL 10 150.50"
        )
        return

    # Add to portfolio
    try:
        portfolio_service: PortfolioService = context.bot_data.get("portfolio_service")
        if not portfolio_service:
            logger.error("Portfolio service not initialized")
            await update.message.reply_text(
                "⚠️ Service temporarily unavailable. Please try again later."
            )
            return

        await portfolio_service.add_holding(
            user_id=user.id,
            symbol=symbol,
            quantity=quantity,
            purchase_price=price
        )

        total_cost = quantity * price
        await update.message.reply_text(
            f"✅ Added to portfolio!\n\n"
            f"📈 {symbol}\n"
            f"├ Quantity: {quantity}\n"
            f"├ Price: ${price:.2f}\n"
            f"└ Total Cost: ${total_cost:.2f}\n\n"
            f"Use /portfolio to view your holdings."
        )
        logger.info(f"User {user.id} added {quantity} {symbol} at ${price}")

    except Exception as e:
        logger.error(f"Error adding holding for user {user.id}: {e}")
        await update.message.reply_text(
            "⚠️ Failed to add stock. Please try again."
        )
