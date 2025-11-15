# Use uv run, never python
# Prefer async over sync patterns
# Write at 9th grade level in documentation
# Avoid heavily mocking tests without user permission
# Update docs when code changes
# Never git add ., specify files
# Run linters/formatters before committing
# Type check before merging
# Run affected tests for changed files

## Deployment

### Production App
- **URL**: https://avs20--spelling-app-v2-fastapi-app.modal.run
- **Branch**: `modal-deployment`
- **Database**: Production Turso database
- **Description**: Live app for users. Only merge tested code from preprod.

### Preprod (Staging) App
- **URL**: https://avs20--spelling-app-preprod-fastapi-app.modal.run
- **Branch**: `preprod`
- **Database**: Preprod Turso database
- **Description**: Testing environment. Merge feature branches here first to test, then merge to production if everything works.

## Deployment Workflow
1. Create feature branch from `preprod`
2. Merge PR to `preprod` → auto-deploys to preprod app
3. Test at preprod URL
4. Create PR: `preprod` → `modal-deployment`
5. Merge PR → auto-deploys to production app