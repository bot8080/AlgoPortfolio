# CLAUDE.md - AlgoPortfolio

## Project Overview

**AlgoPortfolio** is a Telegram Mini App for stock portfolio analysis and tracking.

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: MVP** | ✅ Complete | Basic bot with `/start`, `/help`, `/analyze` |
| **Phase 2: Portfolio** | 🚧 Current | Database, holdings, P&L tracking |
| **Phase 3: Mini App** | 📋 Planned | React frontend, TradingView charts |
| **Phase 4: Advanced** | 📋 Planned | Technical indicators, alerts |

---

## 🚀 Claude Code Superpowers

This project is configured with skills, agents, and hooks to accelerate development. **Use these instead of doing things manually!**

### Available Skills (Slash Commands)

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/db-setup` | Creates SQLite database infrastructure | Starting Phase 2, need database |
| `/add-command <name> "<desc>"` | Scaffolds new bot command with tests | Adding any new Telegram command |
| `/feature "<description>"` | Plans & implements complete features | Multi-component features |
| `/review` | Code quality check before committing | Before every commit |
| `/test` | Runs full test suite | After any code change |
| `/lint` | Checks code style (flake8, black) | Quick style check |
| `/coverage` | Tests with coverage report | Finding untested code |
| `/test-bot` | Tests bot handlers only | Quick bot validation |

### When Claude Should Suggest Skills

**IMPORTANT:** When I ask you to do something, suggest the appropriate skill:

| If User Says... | Suggest... |
|-----------------|------------|
| "Add a portfolio command" | `/add-command portfolio "View your holdings"` |
| "Set up the database" | `/db-setup` |
| "Add buy/sell tracking" | `/feature "track buy/sell transactions"` |
| "Check my code" | `/review` |
| "Run tests" | `/test` |
| "I want to add X feature" | `/feature "X feature description"` |

### Specialized Agents

These agents are invoked automatically when needed:

| Agent | Specialty | Triggered By |
|-------|-----------|--------------|
| `database-designer` | Schema design, migrations, models | Database/schema tasks |
| `feature-builder` | End-to-end feature implementation | Complex multi-file features |
| `test-writer` | Comprehensive test generation | Writing tests |
| `code-reviewer` | Quality and security review | Code review tasks |

### Automatic Hooks

| Trigger | Action | Benefit |
|---------|--------|---------|
| After editing `.py` files | Syntax check (`py_compile`) | Catch errors immediately |

---

## 📋 Phase 2: Portfolio Dashboard (Current Focus)

### What We're Building

1. **SQLite Database** - Store user portfolios, holdings, transactions
2. **Portfolio Commands** - `/portfolio`, `/add`, `/sell`, `/history`
3. **P&L Calculations** - Track profit/loss per holding and total
4. **Transaction History** - Record all buys and sells

### Phase 2 Workflow

```
Step 1: /db-setup
        → Creates database infrastructure
        → Models: Portfolio, Holding, Transaction
        → Repository with CRUD operations

Step 2: /add-command portfolio "View your stock holdings"
        → Creates /portfolio command
        → Shows holdings with current values

Step 3: /add-command add "Add stock to portfolio"
        → Creates /add command
        → Usage: /add AAPL 10 150.50

Step 4: /add-command sell "Record a stock sale"
        → Creates /sell command
        → Usage: /sell AAPL 5 175.00

Step 5: /feature "calculate P&L for portfolio"
        → Adds P&L calculation service
        → Updates /portfolio to show gains/losses

Step 6: /review → /test → commit
```

### Phase 2 Checklist

- [ ] Database setup (`/db-setup`)
- [ ] Portfolio model & repository
- [ ] `/portfolio` command - view holdings
- [ ] `/add` command - add stock
- [ ] `/sell` command - sell stock
- [ ] `/history` command - transaction history
- [ ] P&L calculations
- [ ] Tests for all new code

---

## 🏗️ Project Structure

```
AlgoPortfolio/
├── .claude/                  # Claude Code configuration
│   ├── settings.json         # Hooks, permissions, project config
│   ├── skills/               # Slash command definitions
│   │   ├── db-setup/
│   │   ├── add-command/
│   │   ├── feature/
│   │   ├── review/
│   │   ├── test/
│   │   ├── lint/
│   │   └── coverage/
│   └── agents/               # Specialized agent definitions
│       ├── database-designer.md
│       ├── feature-builder.md
│       ├── test-writer.md
│       └── code-reviewer.md
│
├── bot/                      # Telegram bot
│   ├── __init__.py
│   └── handlers/             # Command handlers
│       ├── __init__.py
│       ├── start.py          # /start, /help
│       └── analysis.py       # /analyze
│
├── services/                 # Business logic
│   ├── __init__.py
│   ├── market_data/          # Stock data providers
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract provider interface
│   │   └── yfinance_provider.py
│   └── database/             # Database layer (Phase 2)
│       ├── __init__.py
│       ├── connection.py     # SQLite connection manager
│       └── portfolio_repo.py # Portfolio CRUD operations
│
├── models/                   # Data models
│   ├── __init__.py
│   ├── stock.py              # StockPrice, StockInfo, AnalysisResult
│   └── portfolio.py          # Portfolio, Holding, Transaction (Phase 2)
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── logger.py             # Logging setup
│   └── exceptions.py         # Custom exceptions
│
├── tests/                    # Test files
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_handlers.py
│   ├── test_market_data.py
│   └── test_models.py
│
├── data/                     # Database files (Phase 2, gitignored)
│   └── portfolio.db
│
├── main.py                   # Entry point
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment template
├── .env                      # Your config (git ignored)
└── CLAUDE.md                 # This file
```

---

## 🔧 Development Workflow

### Standard Workflow

```
1. Describe what you want to build
2. Claude suggests appropriate skill/approach
3. Use skill or let Claude implement
4. /review - check code quality
5. /test - verify tests pass
6. Commit changes
```

### Adding a New Bot Command

**DON'T:** Manually create files, forget to register, skip tests

**DO:** Use the skill!
```
/add-command <name> "<description>"
```

This automatically:
- Creates `bot/handlers/{name}.py` with proper pattern
- Exports from `bot/handlers/__init__.py`
- Registers in `main.py`
- Updates help message in `start.py`
- Creates `tests/test_{name}.py`

### Adding a Complex Feature

**DON'T:** Jump straight into coding without a plan

**DO:** Use the feature skill!
```
/feature "description of what you want"
```

This will:
1. Analyze requirements
2. Present implementation plan
3. Create all components (db, service, command, tests)
4. Validate each step

### Before Committing

**ALWAYS** run:
```
/review    # Check code quality
/test      # Verify tests pass
```

---

## 📐 Architecture

### Data Flow

```
User sends command
         ↓
Bot Handler (bot/handlers/)
         ↓
Service Layer (services/)
    ├── Market Data → YFinance API
    └── Database → SQLite (Phase 2)
         ↓
Models (models/)
         ↓
Format Response
         ↓
Send to User
```

### Layer Responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Handlers** | `bot/handlers/` | Parse input, call services, format output |
| **Services** | `services/` | Business logic, external APIs, data access |
| **Models** | `models/` | Data structures, validation |
| **Utils** | `utils/` | Logging, exceptions, helpers |

### Key Patterns

**Handler Pattern:**
```python
async def command_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"User {user.id} used /command")

    try:
        result = await service.do_something()
        await update.message.reply_text(format_result(result))
    except CustomError as e:
        await update.message.reply_text(f"⚠️ {e.message}")
```

**Service Pattern:**
```python
class SomeService:
    def __init__(self, repository: Repository):
        self._repo = repository

    async def business_operation(self, params) -> Result:
        # Validation, business logic, persistence
        pass
```

**Model Pattern:**
```python
@dataclass
class ModelName:
    required_field: str
    optional_field: Optional[str] = None
    id: Optional[int] = None
```

---

## 🧪 Testing

### Quick Commands

| Command | Purpose |
|---------|---------|
| `/test` | Run all tests |
| `/test-bot` | Run bot handler tests only |
| `/coverage` | Tests with coverage report |

### Test Conventions

- Tests in `tests/` directory
- File naming: `test_{module}.py`
- Use `pytest.mark.asyncio` for async tests
- Mock external dependencies (Telegram, APIs)
- Test success AND error paths

### Running Tests Manually

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=term-missing

# Specific file
pytest tests/test_handlers.py -v

# Specific test
pytest tests/test_handlers.py::TestAnalyzeCommand -v
```

---

## 📝 Coding Standards

### Python Style
- PEP 8 compliant
- Type hints on ALL functions
- Async/await for I/O operations
- Docstrings for public functions

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Imports Order
```python
# Standard library
from datetime import datetime
from typing import Optional

# Third-party
from telegram import Update

# Local
from models.stock import StockPrice
from utils.logger import get_logger
```

### Error Handling
- Use custom exceptions from `utils/exceptions.py`
- User-friendly messages (with emojis)
- Log errors with context
- Never expose internal errors to users

### Commits
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Brief, descriptive messages
- No Claude signatures

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional (future phases)
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=

# Development
LOG_LEVEL=INFO
DEBUG=false
```

### Quick Start

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

# Run
python main.py

# Test
pytest tests/ -v
```

---

## 📊 Bot Commands Reference

### Current Commands (Phase 1)

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message | `/start` |
| `/help` | List commands | `/help` |
| `/analyze` | Stock analysis | `/analyze AAPL` |

### Phase 2 Commands (To Build)

| Command | Description | Example |
|---------|-------------|---------|
| `/portfolio` | View holdings | `/portfolio` |
| `/add` | Add stock | `/add AAPL 10 150.50` |
| `/sell` | Sell stock | `/sell AAPL 5 175.00` |
| `/history` | Transaction history | `/history` |

### Phase 3+ Commands (Future)

| Command | Description |
|---------|-------------|
| `/watchlist` | Manage watchlist |
| `/alert` | Set price alerts |
| `/search` | Search stocks |
| `/chart` | View charts (Mini App) |

---

## 🗺️ Roadmap

### Phase 1: MVP ✅
- [x] Project structure
- [x] `/start`, `/help` commands
- [x] YFinance integration
- [x] `/analyze` command
- [x] Comprehensive tests (51 passing)

### Phase 2: Portfolio 🚧
- [ ] SQLite database setup
- [ ] Portfolio, Holding, Transaction models
- [ ] `/portfolio` command
- [ ] `/add` command
- [ ] `/sell` command
- [ ] `/history` command
- [ ] P&L calculations
- [ ] Full test coverage

### Phase 3: Mini App 📋
- [ ] FastAPI backend
- [ ] React frontend
- [ ] TradingView charts
- [ ] Telegram Mini App integration

### Phase 4: Advanced 📋
- [ ] Technical indicators (RSI, MACD)
- [ ] Pattern detection
- [ ] Price alerts
- [ ] Multi-provider fallback

---

## 🔗 Useful Links

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [YFinance docs](https://github.com/ranaroussi/yfinance)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [aiosqlite docs](https://aiosqlite.omnilib.dev/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

---

## 💡 Quick Reminders for Claude

When working on this project, remember:

1. **Suggest skills first** - If user wants to add a command, suggest `/add-command`. For features, suggest `/feature`.

2. **Always run quality checks** - Remind user to run `/review` and `/test` before committing.

3. **Follow patterns** - Use existing code as templates (analysis.py for handlers, stock.py for models).

4. **Phase 2 focus** - We're building the portfolio dashboard. Database → Commands → P&L.

5. **Test everything** - Every new feature needs tests. Use `/coverage` to find gaps.

6. **Keep it simple** - Don't over-engineer. Build what's needed for the current phase.

### Suggested Responses

If user seems stuck:
> "Would you like me to run `/db-setup` to create the database infrastructure for Phase 2?"

If user asks to add a command:
> "I can scaffold that with `/add-command <name> "<description>"`. Want me to proceed?"

If user finished implementing:
> "Let's run `/review` to check code quality and `/test` to verify everything works."

If user asks what to do next:
> "Based on the Phase 2 checklist, the next step is [X]. Want me to help with that?"
