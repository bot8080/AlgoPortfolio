"""
AlgoPortfolio - Telegram Stock Analysis Bot

Entry point for the application.
"""

import sys
from telegram.ext import Application, CommandHandler

from config import Config
from bot.handlers import (
    start_command,
    help_command,
    analyze_command,
    portfolio_command,
    add_command,
    sell_command,
    history_command,
)
from services.database.connection import DatabaseManager
from services.database.portfolio_repo import PortfolioRepository
from services.database.portfolio_service import PortfolioService
from services.market_data.yfinance_provider import YFinanceProvider
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(
    name="algoportfolio",
    level=Config.get_log_level(),
    log_file=Config.LOG_FILE,
)


async def post_init(application: Application) -> None:
    """Initialize database and dependencies after application starts.

    Args:
        application: The Telegram application instance
    """
    logger.info("Initializing database...")

    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.init_tables()

    # Create repository and provider
    repo = PortfolioRepository(db_manager)
    provider = YFinanceProvider()

    # Create service layer
    portfolio_service = PortfolioService(repo)

    # Store in bot_data for handlers to access
    application.bot_data["db_manager"] = db_manager
    application.bot_data["portfolio_repo"] = repo
    application.bot_data["portfolio_service"] = portfolio_service
    application.bot_data["market_provider"] = provider

    logger.info("Database and services initialized successfully")


def main() -> None:
    """Start the bot."""
    logger.info("=" * 50)
    logger.info("Starting AlgoPortfolio Bot")
    logger.info("=" * 50)

    # Validate configuration
    try:
        Config.validate()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Create application with post_init callback
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("sell", sell_command))
    application.add_handler(CommandHandler("history", history_command))

    # Log registered commands
    logger.info("Registered commands: /start, /help, /analyze, /portfolio, /add, /sell, /history")

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
