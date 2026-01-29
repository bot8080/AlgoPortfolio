---
name: test
description: Run the full test suite. Use after code changes to validate everything works.
allowed-tools: Bash, Read, Grep
---

# Test Skill

Run the complete test suite for AlgoPortfolio.

## Instructions

1. Run pytest with verbose output:
   ```bash
   pytest tests/ -v
   ```

2. If tests fail:
   - Report which tests failed
   - Show the error messages
   - Suggest potential fixes based on the error

3. If all tests pass:
   - Report the total number of tests run
   - Confirm all passed

## Notes
- Tests may make real API calls (YFinance)
- Some tests are async and require pytest-asyncio
- Run from the project root directory
