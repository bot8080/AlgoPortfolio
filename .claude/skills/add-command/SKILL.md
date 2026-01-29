---
name: add-command
description: Scaffold a new Telegram bot command with handler, registration, help text, and tests.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Add Command Skill

Scaffold a new Telegram bot command following AlgoPortfolio patterns.

## Usage

```
/add-command <name> "<description>"
```

Examples:
- `/add-command portfolio "View your stock holdings"`
- `/add-command add "Add a stock to your portfolio"`
- `/add-command watchlist "Manage your watchlist"`

## Instructions

### Step 1: Parse Arguments
Extract the command name and description from the user's input.
- Command name should be lowercase, valid Python identifier
- Description should be a short phrase

### Step 2: Create Handler File
Create `bot/handlers/{name}.py` following this template:

```python
"""
Handler for /{name} command.
{description}
"""
from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import get_logger

logger = get_logger(__name__)


async def {name}_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /{name} command - {description}."""
    user = update.effective_user
    logger.info(f"User {user.id} used /{name}")

    # TODO: Implement command logic
    await update.message.reply_text(
        f"📊 {description}\n\n"
        "This feature is coming soon!"
    )
```

### Step 3: Update Handler Exports
Add to `bot/handlers/__init__.py`:
```python
from .{name} import {name}_command
```

And add to `__all__` list.

### Step 4: Register Command in main.py
Add import and handler registration:
```python
from bot.handlers.{name} import {name}_command
# In the main() function:
app.add_handler(CommandHandler("{name}", {name}_command))
```

### Step 5: Update Help Message
In `bot/handlers/start.py`, add to the help_command function's response:
```
/{name} - {description}
```

### Step 6: Create Test File
Create `tests/test_{name}.py`:

```python
"""Tests for /{name} command handler."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.{name} import {name}_command


@pytest.fixture
def mock_update():
    """Create mock Telegram Update."""
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram Context."""
    context = MagicMock()
    context.args = []
    return context


@pytest.mark.asyncio
async def test_{name}_command(mock_update, mock_context):
    """Test /{name} command responds."""
    await {name}_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    response = mock_update.message.reply_text.call_args[0][0]
    assert "{description}" in response or "coming soon" in response.lower()
```

### Step 7: Verify
- Run `python -m py_compile bot/handlers/{name}.py`
- Run `pytest tests/test_{name}.py -v`

## Conventions
- Handler function: `{name}_command`
- Always log user ID on command use
- Use emojis in responses (📊, ✅, ❌, ⚠️)
- Handle errors with user-friendly messages
- Tests use pytest with asyncio marker
