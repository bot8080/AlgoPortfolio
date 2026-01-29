---
name: test-bot
description: Run tests for Telegram bot handlers only. Use to quickly validate bot command changes.
allowed-tools: Bash, Read, Grep
---

# Test Bot Skill

Run tests specifically for Telegram bot handlers.

## Instructions

1. Run handler tests only:
   ```bash
   pytest tests/test_handlers.py -v
   ```

2. If tests fail:
   - Report which handler tests failed
   - Show the error messages
   - Check if mock setup is correct

3. If all tests pass:
   - Report the number of handler tests run
   - Confirm bot handlers are working

## Notes
- Handler tests use mocks for Telegram API
- No real Telegram API calls are made
- Tests cover /start, /help, and /analyze commands
