---
name: coverage
description: Run tests with coverage report. Use to identify untested code paths.
allowed-tools: Bash, Read, Grep
---

# Coverage Skill

Run tests with code coverage analysis.

## Instructions

1. Run pytest with coverage:
   ```bash
   pytest tests/ --cov=bot --cov=services --cov=models --cov=utils --cov-report=term-missing
   ```

2. Analyze the report:
   - Show overall coverage percentage
   - Identify files with low coverage (<80%)
   - List specific uncovered lines for critical files

3. Provide recommendations:
   - Suggest which functions need more tests
   - Prioritize based on code criticality

## Notes
- Target coverage: 80%+ for core modules
- `term-missing` shows which lines are not covered
- Focus on business logic in services/ and handlers
