---
name: review
description: Code quality check with style, type hints, security, and test coverage review.
allowed-tools: Bash, Read, Grep, Glob
---

# Code Review Skill

Perform comprehensive code quality check before committing.

## Usage

```
/review              # Review all changed files
/review <path>       # Review specific file or directory
```

## Instructions

### Step 1: Identify Files to Review

Check git status for changed files:
```bash
git status --short
```

Or if a specific path is given, focus on that.

### Step 2: Run Automated Checks

```bash
# Formatting check (if black installed)
black --check --diff .

# Import sorting (if isort installed)
isort --check-only --diff .

# Linting
flake8 . --count --statistics --max-line-length=100
```

### Step 3: Manual Code Review

For each changed file, check:

**Style**
- [ ] PEP 8 compliant
- [ ] Consistent naming conventions
- [ ] Imports organized (stdlib, third-party, local)
- [ ] No unused imports/variables

**Type Hints**
- [ ] All function parameters typed
- [ ] All return types specified
- [ ] Optional used for nullable values

**Documentation**
- [ ] Public functions have docstrings
- [ ] Complex logic has comments

**Error Handling**
- [ ] Specific exceptions (not bare except)
- [ ] User-friendly error messages
- [ ] Errors logged with context

**Security**
- [ ] No hardcoded secrets
- [ ] SQL uses parameterized queries
- [ ] User input validated

### Step 4: Check Test Coverage

```bash
pytest --cov=. --cov-report=term-missing tests/
```

Target: 80%+ coverage for new code.

### Step 5: Report Results

Format results as:

```
📋 Code Review Report
=====================

📁 Files Reviewed: {count}
   - {file1} (new/modified)
   - {file2} (modified)

✅ Style Checks
   - black: PASSED/FAILED
   - isort: PASSED/FAILED
   - flake8: {count} issues

⚠️ Quality Issues ({count})
   1. {file}:{line}
      {issue description}

🔒 Security: PASSED/issues found

📊 Test Coverage: {percent}%

📝 Recommendations:
   1. {recommendation}
   2. {recommendation}

Overall: ✅ Ready to commit / ⚠️ Fix issues first
```

## Auto-Fix Option

If user wants auto-fixes:
```bash
black .
isort .
```

Then re-run checks.

## Project-Specific Checks

### Handler Files (bot/handlers/*.py)
- Logs user ID on command use
- Handles missing/invalid arguments
- Uses emojis consistently

### Service Files (services/*.py)
- Async methods for I/O
- Raises appropriate exceptions
- Has logging

### Model Files (models/*.py)
- Uses @dataclass
- All fields have type hints
- Follows existing patterns

### Test Files (tests/*.py)
- Uses pytest.mark.asyncio
- Mocks external dependencies
- Tests success AND error cases
