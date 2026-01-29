---
name: lint
description: Check code style with flake8 and black. Use to ensure code quality standards.
allowed-tools: Bash, Read, Grep
---

# Lint Skill

Check code style and formatting for AlgoPortfolio.

## Instructions

1. Run flake8 for style violations:
   ```bash
   flake8 bot/ services/ models/ utils/ tests/ --max-line-length=100 --ignore=E501,W503
   ```

2. Check black formatting:
   ```bash
   black --check bot/ services/ models/ utils/ tests/
   ```

3. If violations found:
   - Report the files and line numbers with issues
   - Describe what needs to be fixed
   - Optionally suggest running `black .` to auto-fix formatting

4. If all checks pass:
   - Confirm code style is clean

## Notes
- flake8 checks PEP 8 compliance
- black checks code formatting
- Line length limit is 100 characters
- E501 (line too long) is ignored for flexibility
