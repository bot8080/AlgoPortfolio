"""
AlgoPortfolio - Telegram Stock Analysis Bot

Entry point for the application.
"""

import sys
from telegram.ext import Application, CommandHandler

from config import Config
from bot.handlers import start_command, help_command, analyze_command
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(
    name="algoportfolio",
    level=Config.get_log_level(),
    log_file=Config.LOG_FILE,
)


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

    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))

    # Log registered commands
    logger.info("Registered commands: /start, /help, /analyze")

    # Start the bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
