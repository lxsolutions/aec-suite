



# Contributing to Rover Operations

Thank you for your interest in contributing to the Rover Operations project! This document provides guidelines for contributing code, documentation, and other improvements.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Commit Guidelines](#commit-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Testing](#testing)
8. [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct that promotes respectful and inclusive collaboration. By participating in this project, you agree to uphold these principles.

## Getting Started

### Issues
- Check the existing issues before creating new ones
- Use issue templates for bug reports, features, or tasks
- Provide detailed information when reporting issues

### Forking and Cloning
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rover-operations.git
   cd rover-operations
   ```

## Development Setup

### Prerequisites
- Docker
- Make
- Node.js 20+
- Go 1.22+
- Python 3.11+

### Environment Setup
```bash
# Install dependencies for all services
make dev up

# Verify setup by running tests (when available)
make test
```

## Coding Standards

### General Principles
- Write clean, maintainable code with clear documentation
- Follow the existing style and patterns in each language/service
- Prioritize safety and reliability over clever optimizations

### Language-specific Guidelines

#### Go
- Use gofmt for consistent formatting
- Follow Go idioms and best practices
- Add comprehensive comments for complex logic

#### TypeScript/Next.js
- Use Prettier for code formatting
- Follow React best practices
- Write type-safe code with proper interfaces

#### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions

## Commit Guidelines

### Commit Message Format
Use the conventional commit format:
```
<type>(<scope>): <subject>

<body>
```

Example:
```
feat(control-broker): add session timeout handling

Implement automatic session termination after inactivity.
Closes #123
```

### Types of Commits
- `feat`: New feature or enhancement
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting, whitespace changes
- `refactor`: Code improvements without functional changes
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

## Pull Request Process

1. **Create a branch**: Use descriptive names like `feature/control-session-timeout`
2. **Make commits**: Follow the commit guidelines above
3. **Rebase regularly**: Keep your branch up-to-date with main
4. **Write tests**: Ensure all new functionality is properly tested
5. **Update documentation**: If applicable, update relevant docs

### Pull Request Template
- Describe the problem being solved
- Explain how to test the changes
- Reference any related issues (e.g., "Closes #123")
- Add screenshots/gifs if visual changes are involved

## Testing

### Unit Tests
- Write unit tests for all new functionality
- Ensure existing tests pass before submitting PRs
- Use appropriate testing frameworks:
  - Go: `testing` package or `testify`
  - TypeScript: Jest
  - Python: pytest

### Integration Tests
- Develop integration tests for critical workflows
- Test end-to-end scenarios when possible

## Documentation

### Code Documentation
- Add comments and docstrings to explain complex logic
- Document public APIs thoroughly
- Keep inline documentation up-to-date with code changes

### User Documentation
- Update README.md for significant new features
- Add or update markdown files in the `docs/` directory
- Include diagrams using Mermaid syntax when helpful

## Development Workflow

1. **Explore**: Understand the existing codebase and architecture
2. **Plan**: Break down work into manageable tasks
3. **Implement**: Write clean, well-tested code
4. **Review**: Self-review before submitting PRs
5. **Iterate**: Incorporate feedback from reviewers

## Community Engagement

- Participate in discussions on issues and pull requests
- Help review other contributors' work
- Share your knowledge through documentation and examples

Thank you for contributing to Rover Operations! Your efforts help make this project better for everyone.

