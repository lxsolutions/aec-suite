


# ADR 0001: Monorepo Structure for AEC Suite

## Status

Accepted

## Context

The AEC Suite consists of multiple interconnected services and applications that were previously maintained in separate repositories:
- aec-orchestrator
- rover-operations  
- buildforge-cloud
- estatejoint
- atlas-erp

This fragmentation led to:
- Inconsistent development practices
- Duplicated effort and code
- Complex dependency management
- Difficult cross-service testing and development
- Inefficient CI/CD pipelines

## Decision

We will consolidate all AEC Suite components into a single monorepo with the following structure:

```
aec-suite/
├── apps/
│   └── estatejoint/          # UI applications
├── services/
│   ├── orchestrator/         # Core orchestration service
│   ├── rover/               # Rover operations service
│   ├── buildforge/          # CI/CD infrastructure
│   └── erp-bridge/          # ERP integration service
├── libs/                    # Shared libraries (TS, Python, Go)
├── schemas/                 # Protocol definitions
├── infra/                   # Infrastructure as Code
├── tools/                   # Development tools
├── docs/                    # Documentation
└── .github/                 # CI/CD workflows
```

### Technology Choices

- **Package Management**: pnpm workspaces for JS/TS, uv for Python
- **Build System**: TurboRepo for task orchestration
- **Development**: DevContainer with Docker-in-Docker
- **CI/CD**: GitHub Actions with matrix builds
- **Code Quality**: Pre-commit hooks with unified linting

### Git Strategy

- Use `git subtree` to preserve full history from source repositories
- Maintain original commit authors and timestamps
- Namespace tags if necessary to avoid conflicts

## Consequences

### Positive

- **Improved Developer Experience**: Single setup, consistent tooling
- **Better Code Sharing**: Shared libraries and utilities
- **Unified CI/CD**: Single pipeline for all services
- **Easier Refactoring**: Cross-service changes in single PR
- **Consistent Standards**: Unified linting, testing, and formatting

### Negative

- **Initial Migration Complexity**: One-time effort to consolidate
- **Larger Repository Size**: All history preserved
- **Learning Curve**: Developers need to adapt to monorepo patterns

### Risks

- **Build Times**: Could increase without proper caching
- **Tooling Complexity**: Requires robust workspace management
- **Permission Management**: Fine-grained access control needed

## Migration Plan

1. Initialize monorepo with empty commit
2. Add all source repos as remotes and fetch
3. Use `git subtree add` to merge each repository
4. Set up workspace configurations
5. Create DevContainer and development tooling
6. Establish CI/CD pipelines
7. Document structure and migration details

## Alternatives Considered

### Polyrepo Approach (Current State)
- **Pros**: Independent versioning, smaller repos
- **Cons**: Fragmented development, dependency hell, duplicated effort

### Git Submodules
- **Pros**: History separation, independent development
- **Cons**: Complex workflow, submodule drift, poor developer experience

### Bazel Monorepo
- **Pros**: Excellent build performance, hermetic builds
- **Cons**: Steep learning curve, complex configuration

## Implementation Details

- Root package.json with pnpm workspaces
- TurboRepo for task orchestration
- UV for Python package management
- DevContainer with full toolchain
- GitHub Actions with matrix builds
- Pre-commit hooks for code quality

## References

- [TurboRepo Documentation](https://turbo.build/repo)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [UV Python Package Manager](https://github.com/astral-sh/uv)
- [Git Subtree](https://www.atlassian.com/git/tutorials/git-subtree)


