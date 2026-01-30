"""
Handler for /sell command.
Sell stock from your portfolio.
"""
from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.ext import ContextTypes

from services.database import PortfolioService
from utils.logger import get_logger

logger = get_logger(__name__)


async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sell command - Sell stock from your portfolio.

    Usage: /sell SYMBOL QUANTITY PRICE
    Example: /sell AAPL 5 175.00
    """
    user = update.effective_user
    logger.info(f"User {user.id} used /sell")

    # Check arguments
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Invalid usage.\n\n"
            "Usage: /sell SYMBOL QTY PRICE\n"
            "Example: /sell AAPL 5 175.00"
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
            "Example: /sell AAPL 5 175.00"
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
            "Example: /sell AAPL 5 175.00"
        )
        return

    # Sell from portfolio
    try:
        portfolio_service: PortfolioService = context.bot_data.get("portfolio_service")
        if not portfolio_service:
            logger.error("Portfolio service not initialized")
            await update.message.reply_text(
                "⚠️ Service temporarily unavailable. Please try again later."
            )
            return

        holding = await portfolio_service.sell_holding(
            user_id=user.id,
            symbol=symbol,
            quantity=quantity,
            sell_price=price
        )

        # Stock not found in portfolio
        if holding is None:
            await update.message.reply_text(
                f"❌ You don't own any {symbol}.\n\n"
                "Use /portfolio to see your current holdings."
            )
            return

        total_proceeds = quantity * price

        # Check if position fully closed
        if holding.quantity <= 0:
            await update.message.reply_text(
                f"✅ Position closed!\n\n"
                f"📉 {symbol}\n"
                f"├ Sold: {quantity} shares\n"
                f"├ Price: ${price:.2f}\n"
                f"└ Total Proceeds: ${total_proceeds:.2f}\n\n"
                f"Position fully liquidated."
            )
        else:
            await update.message.reply_text(
                f"✅ Sold from portfolio!\n\n"
                f"📉 {symbol}\n"
                f"├ Sold: {quantity} shares\n"
                f"├ Price: ${price:.2f}\n"
                f"├ Proceeds: ${total_proceeds:.2f}\n"
                f"└ Remaining: {holding.quantity:.2f} shares\n\n"
                f"Use /portfolio to view your holdings."
            )

        logger.info(f"User {user.id} sold {quantity} {symbol} at ${price}")

    except ValueError as e:
        # Selling more than owned
        await update.message.reply_text(f"❌ {str(e)}")

    except Exception as e:
        logger.error(f"Error selling holding for user {user.id}: {e}")
        await update.message.reply_text(
            "⚠️ Failed to sell stock. Please try again."
        )
