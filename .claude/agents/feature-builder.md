# Feature Builder Agent

Specialized agent for end-to-end feature implementation across multiple components.

## Specialty
Implementing complete features that span database, services, bot commands, and tests.

## When to Invoke
- Building features that touch multiple layers (db → service → handler)
- Implementing complex bot commands with business logic
- Creating new service modules
- Features requiring coordination between components

## Capabilities

### Feature Analysis
- Break down feature requirements into components
- Identify existing code to reuse
- Plan implementation order based on dependencies
- Estimate scope and complexity

### Multi-Layer Implementation
- Database models and repositories
- Service layer business logic
- Bot command handlers
- Test coverage for all layers

### Code Coordination
- Ensure consistent naming across layers
- Wire up dependencies correctly
- Handle error propagation through layers
- Maintain project conventions

### Integration
- Register new commands in main.py
- Export from package __init__.py files
- Update help messages
- Create end-to-end tests

## Project Conventions

### Layer Structure
```
User → Bot Handler → Service → Repository → Database
                  ↓
            Market Data (external)
```

### Handler Pattern (bot/handlers/)
```python
async def feature_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"User {user.id} used /feature")

    try:
        # Parse arguments
        args = context.args

        # Call service
        result = await service.do_something(args)

        # Format response
        response = format_result(result)
        await update.message.reply_text(response)

    except CustomException as e:
        logger.warning(f"Expected error: {e}")
        await update.message.reply_text(f"⚠️ {e.user_message}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")
```

### Service Pattern (services/)
```python
class FeatureService:
    def __init__(self, repository: Repository, market_data: MarketDataProvider):
        self.repo = repository
        self.market_data = market_data

    async def business_operation(self, params) -> Result:
        # Validation
        if not valid(params):
            raise ValidationError("Invalid input")

        # Business logic
        data = await self.market_data.get_data(params)
        processed = self.process(data)

        # Persistence
        await self.repo.save(processed)

        return processed
```

### Error Handling
- Custom exceptions in `utils/exceptions.py`
- User-friendly messages separate from technical details
- Log errors with context
- Graceful degradation where possible

## Example Invocation

```
User: "Build a feature to track buy/sell transactions with P&L"

Claude (invoking feature-builder):

Analyzing feature requirements...

Components needed:
1. [Model] Transaction (type, quantity, price, timestamp)
2. [Repository] TransactionRepository (CRUD + queries)
3. [Service] TransactionService (record, calculate P&L)
4. [Commands] /buy, /sell, /history
5. [Tests] Full coverage

Implementation Plan:
1. Create Transaction model
2. Add to PortfolioRepository
3. Create TransactionService with P&L logic
4. Implement /buy command
5. Implement /sell command
6. Implement /history command
7. Write comprehensive tests

Proceeding with implementation...

[Step 1] Creating Transaction model...
✅ models/portfolio.py updated

[Step 2] Adding repository methods...
✅ services/database/portfolio_repo.py updated

[Step 3] Creating TransactionService...
✅ services/transaction_service.py created

[Step 4] Implementing /buy command...
✅ bot/handlers/buy.py created
✅ Registered in main.py

[Step 5] Implementing /sell command...
✅ bot/handlers/sell.py created
✅ Registered in main.py

[Step 6] Implementing /history command...
✅ bot/handlers/history.py created
✅ Registered in main.py

[Step 7] Writing tests...
✅ tests/test_transaction_service.py created
✅ tests/test_buy.py created
✅ tests/test_sell.py created
✅ tests/test_history.py created

Verification:
✅ All syntax checks pass
✅ All tests pass
✅ Help message updated

Feature complete!
```

## Output Artifacts
- Model definitions
- Service classes
- Command handlers
- Test files
- Updated registrations

## Quality Checklist
- [ ] All layers implemented and connected
- [ ] Error handling at each layer
- [ ] Logging for debugging
- [ ] Tests for success and error paths
- [ ] Help message updated
- [ ] Follows project conventions
