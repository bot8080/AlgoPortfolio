"""Tests for stock data models."""

from datetime import datetime

from models.stock import StockPrice, StockInfo, AnalysisResult, Recommendation


class TestStockPrice:
    """Tests for StockPrice dataclass."""

    def test_is_positive_with_positive_change(self, sample_stock_price):
        """Test is_positive returns True for positive change."""
        assert sample_stock_price.is_positive is True

    def test_is_positive_with_negative_change(self, sample_stock_price_negative):
        """Test is_positive returns False for negative change."""
        assert sample_stock_price_negative.is_positive is False

    def test_is_positive_with_zero_change(self):
        """Test is_positive returns True for zero change (no loss)."""
        price = StockPrice(
            symbol="TEST",
            price=100.0,
            change=0.0,
            change_percent=0.0,
            volume=1000,
            timestamp=datetime.now(),
        )
        assert price.is_positive is True

    def test_formatted_change_positive(self, sample_stock_price):
        """Test formatted_change shows + sign for positive change."""
        formatted = sample_stock_price.formatted_change
        assert formatted.startswith("+")
        assert "+2.50" in formatted
        assert "+1.69%" in formatted

    def test_formatted_change_negative(self, sample_stock_price_negative):
        """Test formatted_change shows - sign for negative change."""
        formatted = sample_stock_price_negative.formatted_change
        assert "-5.75" in formatted
        assert "-2.29%" in formatted
        assert not formatted.startswith("+")

    def test_default_currency(self):
        """Test default currency is USD."""
        price = StockPrice(
            symbol="AAPL",
            price=150.0,
            change=1.0,
            change_percent=0.67,
            volume=1000,
            timestamp=datetime.now(),
        )
        assert price.currency == "USD"

    def test_custom_currency(self):
        """Test custom currency can be set."""
        price = StockPrice(
            symbol="SHOP.TO",
            price=100.0,
            change=1.0,
            change_percent=1.0,
            volume=1000,
            timestamp=datetime.now(),
            currency="CAD",
        )
        assert price.currency == "CAD"


class TestStockInfo:
    """Tests for StockInfo dataclass."""

    def test_formatted_market_cap_trillion(self, sample_stock_info):
        """Test market cap formatting for trillions."""
        formatted = sample_stock_info.formatted_market_cap
        assert "$2.50T" == formatted

    def test_formatted_market_cap_billion(self):
        """Test market cap formatting for billions."""
        info = StockInfo(
            symbol="TEST",
            name="Test Corp",
            market_cap=150_000_000_000,  # 150B
        )
        assert info.formatted_market_cap == "$150.00B"

    def test_formatted_market_cap_million(self):
        """Test market cap formatting for millions."""
        info = StockInfo(
            symbol="TEST",
            name="Small Corp",
            market_cap=500_000_000,  # 500M
        )
        assert info.formatted_market_cap == "$500.00M"

    def test_formatted_market_cap_small(self):
        """Test market cap formatting for values under a million."""
        info = StockInfo(
            symbol="TEST",
            name="Micro Corp",
            market_cap=750_000,  # 750K
        )
        assert info.formatted_market_cap == "$750,000"

    def test_formatted_market_cap_none(self, sample_stock_info_minimal):
        """Test market cap formatting when None (ETFs)."""
        assert sample_stock_info_minimal.formatted_market_cap == "N/A"

    def test_optional_fields_default_to_none(self):
        """Test that optional fields default to None."""
        info = StockInfo(symbol="TEST", name="Test Corp")

        assert info.sector is None
        assert info.industry is None
        assert info.market_cap is None
        assert info.pe_ratio is None
        assert info.eps is None
        assert info.dividend_yield is None
        assert info.fifty_two_week_high is None
        assert info.fifty_two_week_low is None
        assert info.average_volume is None
        assert info.description is None


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_confidence_emoji_high(self, sample_stock_price, sample_stock_info):
        """Test high confidence shows green emoji."""
        result = AnalysisResult(
            symbol="AAPL",
            price=sample_stock_price,
            info=sample_stock_info,
            recommendation=Recommendation.STRONG_BUY,
            confidence=85.0,
            summary="Very confident recommendation.",
        )
        assert result.confidence_emoji == "🟢"

    def test_confidence_emoji_medium(self, sample_stock_price, sample_stock_info):
        """Test medium confidence shows yellow emoji."""
        result = AnalysisResult(
            symbol="AAPL",
            price=sample_stock_price,
            info=sample_stock_info,
            recommendation=Recommendation.HOLD,
            confidence=65.0,
            summary="Moderate confidence.",
        )
        assert result.confidence_emoji == "🟡"

    def test_confidence_emoji_low(self, sample_stock_price, sample_stock_info):
        """Test low confidence shows red emoji."""
        result = AnalysisResult(
            symbol="AAPL",
            price=sample_stock_price,
            info=sample_stock_info,
            recommendation=Recommendation.SELL,
            confidence=45.0,
            summary="Low confidence.",
        )
        assert result.confidence_emoji == "🔴"

    def test_confidence_emoji_boundary_80(self, sample_stock_price, sample_stock_info):
        """Test confidence exactly at 80 shows green."""
        result = AnalysisResult(
            symbol="AAPL",
            price=sample_stock_price,
            info=sample_stock_info,
            recommendation=Recommendation.BUY,
            confidence=80.0,
            summary="At boundary.",
        )
        assert result.confidence_emoji == "🟢"

    def test_confidence_emoji_boundary_60(self, sample_stock_price, sample_stock_info):
        """Test confidence exactly at 60 shows yellow."""
        result = AnalysisResult(
            symbol="AAPL",
            price=sample_stock_price,
            info=sample_stock_info,
            recommendation=Recommendation.HOLD,
            confidence=60.0,
            summary="At boundary.",
        )
        assert result.confidence_emoji == "🟡"

    def test_optional_technical_indicators(self, sample_analysis_result):
        """Test that technical indicators default to None."""
        assert sample_analysis_result.rsi is None
        assert sample_analysis_result.macd is None
        assert sample_analysis_result.sma_50 is None
        assert sample_analysis_result.sma_200 is None


class TestRecommendation:
    """Tests for Recommendation enum."""

    def test_all_recommendation_values(self):
        """Test all recommendation enum values exist."""
        assert Recommendation.STRONG_BUY.value == "Strong Buy"
        assert Recommendation.BUY.value == "Buy"
        assert Recommendation.HOLD.value == "Hold"
        assert Recommendation.SELL.value == "Sell"
        assert Recommendation.STRONG_SELL.value == "Strong Sell"

    def test_recommendation_count(self):
        """Test there are exactly 5 recommendation levels."""
        assert len(Recommendation) == 5
