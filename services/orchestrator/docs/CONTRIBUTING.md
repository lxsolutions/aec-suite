








# Contributing to AEC Orchestrator

Thank you for considering contributing to the AEC Orchestrator project! This document outlines our development guidelines and best practices.

## Code Quality Standards

### Backend (Python)
- **Type hints**: All functions must have type annotations
- **Error handling**: Use structured error responses with HTTP status codes
- **Logging**: Implement loguru logging for all critical operations
- **Testing**: Write pytest tests for all new functionality

### Frontend (React/TypeScript)
- **Component structure**: Follow Atomic Design principles
- **State management**: Prefer React Context over Redux where possible
- **Styling**: Use Material UI components with custom themes
- **Testing**: Implement Jest + Testing Library tests

## Development Workflow

1. **Branch naming**: Use `feature/short-description` for new features, `bugfix/issue-number` for fixes
2. **Commit messages**: Follow conventional commits format (type: subject)
3. **Code reviews**: All PRs require at least one approval before merging

## Database Migrations

When making schema changes:
1. Update the SQLAlchemy models in `/backend/src/backend/models.py`
2. Generate a new Alembic migration with `alembic revision --autogenerate -m "description"`
3. Test migrations locally using Docker Compose
4. Include migration scripts in PRs

## Agent Development

When adding or modifying agents:
1. Implement the agent logic in `/agents/` directory
2. Update the coordinator graph in `/backend/src/backend/agents/coordinator.py`
3. Add test cases for new agent functionality
4. Document any new parameters or expected inputs/outputs

## Testing Guidelines

### Backend Tests
- Use `TestClient` from FastAPI to test API endpoints
- Mock external services (ERP, BIM files) where appropriate
- Test both happy paths and error conditions

### Frontend Tests
- Render components in isolation using `@testing-library/react`
- Test form submissions and state changes
- Include accessibility checks with `jest-axe`

## Documentation Standards

- **API endpoints**: Keep Swagger/OpenAPI docs up-to-date
- **User guides**: Maintain clear instructions for common workflows
- **Architecture diagrams**: Update when system design changes significantly

## Security Considerations

1. **Input validation**: Always validate and sanitize user inputs
2. **Authentication**: Use JWT with proper token expiration policies
3. **Data protection**: Encrypt sensitive data both in transit and at rest
4. **Dependency management**: Keep dependencies up-to-date to avoid CVEs



