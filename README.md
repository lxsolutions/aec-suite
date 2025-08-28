


# AEC Suite Monorepo

A unified platform for Architecture, Engineering, and Construction (AEC) orchestration, rover operations, and ERP integration.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (optional, DevContainer recommended)
- pnpm 9+
- uv (Python package manager)

### Development with DevContainer (Recommended)

1. **Open in VS Code with Remote Containers**:
   ```bash
   code .
   # When prompted, "Reopen in Container"
   ```

2. **Or use CLI**:
   ```bash
   make bootstrap
   make dev
   ```

### Manual Setup

1. **Install dependencies**:
   ```bash
   pnpm install
   uv sync --all-workspaces
   ```

2. **Start development services**:
   ```bash
   docker-compose up -d postgres redis nats
   pnpm dev
   ```

## 📁 Repository Structure

```
aec-suite/
├── apps/
│   └── estatejoint/          # EstateJoint application (from estatejoint repo)
├── services/
│   ├── orchestrator/         # AEC Orchestrator (from aec-orchestrator repo)
│   ├── rover/               # Rover Operations (from rover-operations repo)
│   ├── buildforge/          # BuildForge Cloud CI/CD (from buildforge-cloud repo)
│   └── erp-bridge/          # ERP Bridge (from atlas-erp repo)
├── libs/                    # Shared libraries (to be organized)
├── schemas/                 # Protocol schemas (Proto/AsyncAPI)
├── infra/                   # Infrastructure definitions
├── tools/                   # Development tools and scripts
├── docs/                    # Documentation
└── .github/                 # GitHub Actions workflows
```

## 🛠️ Development Commands

```bash
# Install all dependencies
make bootstrap

# Start development environment
make dev

# Run linting
make lint

# Run tests
make test

# Build all packages
make build

# Run type checking
make type-check
```

## 📋 Services Overview

### Apps
- **estatejoint**: Property management and real estate application

### Services
- **orchestrator**: AEC workflow orchestration and automation
- **rover**: Rover operations and simulation
- **buildforge**: CI/CD and DevOps tooling
- **erp-bridge**: ERP system integration (Acumatica/Odoo)

## 🔧 Technology Stack

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Node.js, Python, FastAPI, NestJS
- **Database**: PostgreSQL, Redis
- **Messaging**: NATS, AsyncAPI
- **DevOps**: Docker, GitHub Actions, Terraform
- **Package Management**: pnpm (JS/TS), uv (Python)

## 📚 Documentation

- [Architecture Decision Records (ADRs)](docs/adr/)
- [API Documentation](docs/api/)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages
2. Run `make lint` and `make test` before committing
3. Use pre-commit hooks: `pre-commit install`
4. Create ADRs for significant architectural decisions

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Source Repositories

This monorepo consolidates the following repositories:
- [aec-orchestrator](https://github.com/lxsolutions/aec-orchestrator) → `services/orchestrator/`
- [rover-operations](https://github.com/lxsolutions/rover-operations) → `services/rover/`
- [buildforge-cloud](https://github.com/lxsolutions/buildforge-cloud) → `services/buildforge/`
- [estatejoint](https://github.com/lxsolutions/estatejoint) → `apps/estatejoint/`
- [atlas-erp](https://github.com/lxsolutions/atlas-erp) → `services/erp-bridge/`

Full migration details: [MIGRATION_REPORT.md](MIGRATION_REPORT.md)


