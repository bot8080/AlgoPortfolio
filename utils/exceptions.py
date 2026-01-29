"""Custom exceptions for AlgoPortfolio."""


class AlgoPortfolioError(Exception):
    """Base exception for AlgoPortfolio."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class SymbolNotFoundError(AlgoPortfolioError):
    """Raised when a stock symbol is not found."""

    def __init__(self, symbol: str):
        super().__init__(
            message=f"Symbol '{symbol}' not found",
            details="Please check the symbol and try again",
        )
        self.symbol = symbol


class DataFetchError(AlgoPortfolioError):
    """Raised when data cannot be fetched from provider."""

    def __init__(self, provider: str, reason: str = None):
        super().__init__(
            message=f"Failed to fetch data from {provider}",
            details=reason,
        )
        self.provider = provider


class ConfigurationError(AlgoPortfolioError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, reason: str = None):
        super().__init__(
            message=f"Configuration error for '{config_key}'",
            details=reason or "Please check your .env file",
        )
        self.config_key = config_key


class RateLimitError(AlgoPortfolioError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int = None):
        details = f"Retry after {retry_after} seconds" if retry_after else None
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            details=details,
        )
        self.provider = provider
        self.retry_after = retry_after
