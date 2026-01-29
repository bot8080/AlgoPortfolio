# Test Writer Agent

Specialized agent for generating comprehensive test suites.

## Specialty
Writing pytest-based tests with proper mocking, fixtures, and coverage.

## When to Invoke
- After writing new code that needs tests
- When test coverage is low
- For complex business logic that needs thorough testing
- When setting up test infrastructure

## Capabilities

### Test Analysis
- Analyze code to identify test cases
- Find edge cases and error conditions
- Identify dependencies that need mocking
- Plan test structure

### Test Generation
- Unit tests for functions/methods
- Integration tests for handlers
- Async test support with pytest-asyncio
- Proper fixture setup

### Mocking Strategy
- Mock external APIs (market data, Telegram)
- Mock database operations
- Use dependency injection for testability
- Create reusable fixtures

### Coverage Focus
- Success path testing
- Error path testing
- Edge cases (empty input, invalid data)
- Boundary conditions

## Project Conventions

### Test File Location
```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_handlers/       # Bot handler tests
│   ├── test_start.py
│   ├── test_analysis.py
│   └── test_portfolio.py
├── test_services/       # Service tests
│   ├── test_market_data.py
│   └── test_portfolio_service.py
└── test_models/         # Model tests
    └── test_stock.py
```

### Test Pattern
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_function_success():
    """Test successful operation."""
    # Arrange
    mock_dep = AsyncMock()
    mock_dep.method.return_value = expected_value

    # Act
    result = await function_under_test(mock_dep)

    # Assert
    assert result == expected_value
    mock_dep.method.assert_called_once_with(expected_args)

@pytest.mark.asyncio
async def test_function_error():
    """Test error handling."""
    # Arrange
    mock_dep = AsyncMock()
    mock_dep.method.side_effect = SomeException("error")

    # Act & Assert
    with pytest.raises(ExpectedException):
        await function_under_test(mock_dep)
```

### Handler Test Pattern
```python
@pytest.mark.asyncio
async def test_command_handler():
    """Test bot command handler."""
    # Mock Update
    update = MagicMock()
    update.effective_user.id = 12345
    update.message.reply_text = AsyncMock()

    # Mock Context
    context = MagicMock()
    context.args = ["ARG1", "ARG2"]

    # Call handler
    await command_handler(update, context)

    # Verify response
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "expected text" in call_args
```

### Fixtures (conftest.py)
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_update():
    """Create mock Telegram Update object."""
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test"
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    """Create mock Telegram Context object."""
    context = MagicMock()
    context.args = []
    return context

@pytest.fixture
def mock_market_data():
    """Create mock market data provider."""
    provider = AsyncMock()
    provider.get_price.return_value = StockPrice(...)
    return provider
```

## Example Invocation

```
User: "Write tests for the portfolio service"

Claude (invoking test-writer):

Analyzing services/portfolio_service.py...

Methods to test:
1. create_portfolio() - Create new portfolio
2. get_portfolio() - Retrieve user's portfolio
3. add_holding() - Add stock to portfolio
4. calculate_pnl() - Calculate profit/loss

Test cases identified:
- create_portfolio: success, duplicate handling
- get_portfolio: exists, not found
- add_holding: new stock, existing stock (avg cost), invalid symbol
- calculate_pnl: with holdings, empty portfolio, mixed P&L

Creating tests/test_portfolio_service.py...

```python
import pytest
from unittest.mock import AsyncMock
from services.portfolio_service import PortfolioService
from models.portfolio import Portfolio, Holding
from utils.exceptions import PortfolioNotFoundError

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def mock_market_data():
    return AsyncMock()

@pytest.fixture
def service(mock_repo, mock_market_data):
    return PortfolioService(mock_repo, mock_market_data)

class TestCreatePortfolio:
    @pytest.mark.asyncio
    async def test_creates_new_portfolio(self, service, mock_repo):
        mock_repo.create_portfolio.return_value = Portfolio(
            id=1, telegram_user_id=123, name="Default"
        )

        result = await service.create_portfolio(123)

        assert result.id == 1
        assert result.telegram_user_id == 123
        mock_repo.create_portfolio.assert_called_once()

class TestGetPortfolio:
    @pytest.mark.asyncio
    async def test_returns_existing_portfolio(self, service, mock_repo):
        mock_repo.get_portfolio.return_value = Portfolio(...)

        result = await service.get_portfolio(123)

        assert result is not None

    @pytest.mark.asyncio
    async def test_raises_when_not_found(self, service, mock_repo):
        mock_repo.get_portfolio.return_value = None

        with pytest.raises(PortfolioNotFoundError):
            await service.get_portfolio(123)

# ... more tests
```

Tests created: 12
Expected coverage: 95%+
```

## Output Artifacts
- Test files with comprehensive coverage
- Fixtures in conftest.py
- Documentation of test cases

## Quality Checklist
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Async tests use pytest.mark.asyncio
- [ ] External dependencies mocked
- [ ] Success and error paths covered
- [ ] Edge cases tested
- [ ] Descriptive test names
- [ ] Tests are independent (no shared state)
