---
name: feature
description: Plan and implement a complete feature with database, services, commands, and tests.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Task
---

# Feature Development Skill

Plan and implement a complete feature with all necessary components.

## Usage

```
/feature "<feature description>"
```

Examples:
- `/feature "track buy/sell transactions with P&L calculation"`
- `/feature "add stock to portfolio with quantity and price"`
- `/feature "set price alerts for stocks"`

## Instructions

### Phase 1: Analysis

1. **Understand the feature** - What exactly does the user want?

2. **Identify components needed:**
   - Database models/tables?
   - New bot commands?
   - Service layer logic?
   - External API calls?

3. **Check what exists:**
   - Read relevant existing files
   - Identify code to reuse
   - Find patterns to follow

4. **Create implementation plan** - List ordered steps with dependencies

### Phase 2: Present Plan

Show the user a clear plan before implementing:

```
📋 Feature: {feature description}

Components needed:
1. [Database] {models/tables if needed}
2. [Service] {business logic}
3. [Commands] {bot commands}
4. [Tests] {test coverage}

Implementation order:
1. {First step}
2. {Second step}
3. ...

Estimated changes: {X} new files, {Y} modified files

Proceed? (yes/no)
```

### Phase 3: Implementation

Execute the plan step-by-step:

1. **Create database components** (if needed)
   - Add models to `models/`
   - Add repository methods to `services/database/`
   - Run migrations

2. **Create service layer** (if needed)
   - Add service class to `services/`
   - Implement business logic
   - Handle errors appropriately

3. **Create bot commands** (if needed)
   - Create handlers in `bot/handlers/`
   - Register in `main.py`
   - Update help message

4. **Write tests**
   - Unit tests for services
   - Integration tests for handlers
   - Cover success and error paths

5. **Validate each step**
   - Run syntax check after each file
   - Run relevant tests

### Phase 4: Verification

- All new files syntax-checked
- Imports work correctly
- Tests pass
- Integration verified

## Component Guidelines

### For Database Components
Follow patterns in `services/database/`:
- Use async operations with aiosqlite
- Repository pattern for data access
- Models as dataclasses in `models/`

### For Bot Commands
Follow patterns in `bot/handlers/analysis.py`:
- Async handlers
- Log user actions
- User-friendly error messages
- Register in main.py

### For Services
Follow patterns in `services/market_data/`:
- Async methods for I/O
- Clear interfaces
- Proper error handling
- Logging for debugging

### For Tests
Follow patterns in existing tests:
- pytest with asyncio marker
- Mock external dependencies
- Test success and error paths

## Notes
- For complex features, may invoke specialized agents
- Always verify each step before proceeding
- Keep user informed of progress
- Stop and ask if requirements are unclear
