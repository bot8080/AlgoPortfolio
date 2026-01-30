"""Stock analysis command handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.market_data.yfinance_provider import YFinanceProvider
from models.stock import StockPrice, StockInfo
from utils.exceptions import SymbolNotFoundError, DataFetchError
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize provider
provider = YFinanceProvider()


def format_analysis_message(price: StockPrice, info: StockInfo) -> str:
    """
    Format stock analysis as a Telegram message.

    Args:
        price: Stock price data
        info: Stock information

    Returns:
        Formatted HTML message
    """
    # Determine price trend emoji
    trend_emoji = "📈" if price.is_positive else "📉"
    change_color = "🟢" if price.is_positive else "🔴"

    # Format P/E ratio
    pe_display = f"{info.pe_ratio:.2f}" if info.pe_ratio else "N/A"

    # Format 52-week range
    if info.fifty_two_week_low and info.fifty_two_week_high:
        range_52w = f"${info.fifty_two_week_low:.2f} - ${info.fifty_two_week_high:.2f}"
        # Calculate position in 52-week range
        range_size = info.fifty_two_week_high - info.fifty_two_week_low
        if range_size > 0:
            position = (price.price - info.fifty_two_week_low) / range_size * 100
            range_52w += f" ({position:.0f}%)"
    else:
        range_52w = "N/A"

    # Format dividend yield
    # yfinance may return as decimal (0.0041) or percentage (0.41)
    if info.dividend_yield:
        # Threshold 0.15: yields >15% are rare, so larger values are likely already percentages
        yield_val = info.dividend_yield * 100 if info.dividend_yield < 0.15 else info.dividend_yield
        div_yield = f"{yield_val:.2f}%"
    else:
        div_yield = "N/A"

    message = f"""
{trend_emoji} <b>{info.name}</b> (<code>{price.symbol}</code>)

<b>💰 Price:</b> ${price.price:.2f} {price.currency}
{change_color} <b>Change:</b> {price.formatted_change}

<b>📊 Key Metrics:</b>
├ Market Cap: {info.formatted_market_cap}
├ P/E Ratio: {pe_display}
├ EPS: {f"${info.eps:.2f}" if info.eps else "N/A"}
├ Dividend: {div_yield}
└ 52W Range: {range_52w}

<b>🏢 Company Info:</b>
├ Sector: {info.sector or 'N/A'}
└ Industry: {info.industry or 'N/A'}

<i>⏰ Data as of {price.timestamp.strftime('%Y-%m-%d %H:%M')}</i>
<i>📊 Source: YFinance (15-min delay)</i>
"""
    return message.strip()


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /analyze command - Analyze a stock symbol.

    Usage: /analyze AAPL

    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = update.effective_user.id

    # Check if symbol provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a stock symbol.\n\n"
            "<b>Usage:</b> <code>/analyze AAPL</code>",
            parse_mode="HTML",
        )
        return

    symbol = context.args[0].upper()
    logger.info(f"User {user_id} analyzing: {symbol}")

    # Send "analyzing" message
    status_msg = await update.message.reply_text(
        f"🔍 Analyzing <b>{symbol}</b>...",
        parse_mode="HTML",
    )

    try:
        # Fetch data
        price = await provider.get_price(symbol)
        info = await provider.get_info(symbol)

        # Format and send response
        message = format_analysis_message(price, info)
        await status_msg.edit_text(message, parse_mode="HTML")

        logger.info(f"Analysis complete for {symbol} - ${price.price:.2f}")

    except SymbolNotFoundError:
        logger.warning(f"Symbol not found: {symbol}")
        await status_msg.edit_text(
            f"❌ <b>Symbol not found:</b> <code>{symbol}</code>\n\n"
            "Please check the symbol and try again.\n"
            "<i>Tip: Use standard ticker symbols (AAPL, MSFT, GOOGL)</i>",
            parse_mode="HTML",
        )

    except DataFetchError as e:
        logger.error(f"Data fetch error for {symbol}: {e}")
        await status_msg.edit_text(
            f"⚠️ <b>Error fetching data for {symbol}</b>\n\n"
            f"{e.message}\n"
            "Please try again in a moment.",
            parse_mode="HTML",
        )

    except Exception as e:
        logger.exception(f"Unexpected error analyzing {symbol}: {e}")
        await status_msg.edit_text(
            "❌ <b>An unexpected error occurred</b>\n\n"
            "Please try again later or contact support.",
            parse_mode="HTML",
        )
