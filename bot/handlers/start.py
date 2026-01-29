"""Start and help command handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import get_logger

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - Welcome message.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")

    welcome_message = f"""
👋 <b>Welcome to AlgoPortfolio, {user.first_name}!</b>

I'm your personal stock analysis assistant. I can help you:

📊 <b>Analyze stocks</b> - Get price, fundamentals, and insights
📈 <b>Track markets</b> - Stay updated on your favorite stocks
🔔 <b>Set alerts</b> - Get notified on price movements (coming soon)

<b>Quick Start:</b>
Type <code>/analyze AAPL</code> to analyze Apple stock

Use <code>/help</code> to see all available commands.
"""

    await update.message.reply_text(welcome_message, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /help command - Show available commands.

    Args:
        update: Telegram update object
        context: Bot context
    """
    logger.info(f"User {update.effective_user.id} requested help")

    help_message = """
📚 <b>AlgoPortfolio Commands</b>

<b>Analysis:</b>
/analyze &lt;symbol&gt; - Analyze a stock
  <i>Example: /analyze AAPL</i>

<b>General:</b>
/start - Welcome message
/help - Show this help

<b>Coming Soon:</b>
/portfolio - View your holdings
/alert - Set price alerts
/search - Search for stocks

<b>Tips:</b>
• Use uppercase symbols (AAPL, MSFT, GOOGL)
• US stocks are supported
• Data has ~15 min delay (free tier)

<b>Need help?</b>
Report issues at: github.com/your-repo/issues
"""

    await update.message.reply_text(help_message, parse_mode="HTML")
