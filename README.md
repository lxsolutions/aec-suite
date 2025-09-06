


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

## 🎯 Vertical Slice: Bid→Plan→Bill Workflow

Run the complete vertical slice demonstrating the end-to-end workflow:

1. **Start infrastructure services**:
   ```bash
   make bootstrap
   docker compose up -d postgres redis nats jaeger
   ```

2. **Start the FastAPI gateway**:
   ```bash
   make gateway.run
   # Gateway runs on http://localhost:8080
   ```

3. **Verify gateway health**:
   ```bash
   curl http://localhost:8080/healthz
   # Should return: {"status": "ok"}
   ```

4. **Test the workflow**:
   ```bash
   # Create a project
   curl -X POST http://localhost:8080/v1/projects \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y" \
     -H "Content-Type: application/json" \
     -d '{"name": "Demo Project", "client_id": "demo-client", "budget": 1000000}'

   # Upload an RFP (example file)
   echo "Construction project specifications" > test_rfp.txt
   curl -X POST http://localhost:8080/v1/rfps/ingest \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y" \
     -F "file=@test_rfp.txt" \
     -F "project_id=demo-project-123"

   # Check generated estimate
   curl http://localhost:8080/v1/estimates?project_id=demo-project-123 \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"
   ```

5. **Access observability**:
   - Jaeger UI: http://localhost:16686 (tracing)
   - View distributed traces across services

### Key Components Tested

- ✅ **Gateway**: FastAPI with JWT auth and rate limiting
- ✅ **Events**: NATS messaging for cross-service communication  
- ✅ **Database**: PostgreSQL storage for projects and estimates
- ✅ **Observability**: OpenTelemetry tracing with Jaeger
- ✅ **UI**: EstateJoint Bid→Plan→Bill page integration
- ✅ **ERP Integration**: Stub ERP bridge with NATS consumer

### Environment Variables

Create `.env` file in `services/gateway/`:
```bash
# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key
JWT_ALGORITHM=HS256

# Database
DATABASE_URL=postgresql+asyncpg://aec:aec123@localhost:5432/aec_suite

# NATS
NATS_URL=nats://localhost:4222

# Services
ORCHESTRATOR_URL=http://localhost:3001
ROVER_URL=http://localhost:3002
ERP_BRIDGE_URL=http://localhost:3003
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

## 🚢 Deployment

### Quick Demo
Run a local demo environment with all services:
```bash
make demo
```

This will start:
- Infrastructure services (Postgres, Redis, NATS, Jaeger)
- Gateway service on http://localhost:8080
- ERP Bridge service
- Jaeger UI on http://localhost:16686

Stop the demo with:
```bash
make demo.stop
```

### Docker Images
Multi-arch Docker images are automatically built and pushed to GitHub Container Registry on every push to main/master:

```bash
# Pull specific service image
docker pull ghcr.io/lxsolutions/aec-suite-gateway:latest
docker pull ghcr.io/lxsolutions/aec-suite-erp-bridge:latest
```

### Helm Charts
Helm charts are available in the `deploy/helm` directory:

```bash
# Install ERP Bridge with Helm
helm install erp-bridge deploy/helm/erp-bridge/ \
  --set config.erpAdapter="acumatica" \
  --set config.acumatica.baseUrl="https://your-acumatica-instance.com" \
  --set config.acumatica.username="your-username" \
  --set config.acumatica.password="your-password"
```

### Environment Configuration
Key environment variables for ERP Bridge:
```bash
ERP_ADAPTER=acumatica  # or "odoo", "mock"
NATS_URL=nats://nats:4222
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://aec:aec123@postgresql:5432/aec_suite

# Acumatica specific
ACUMATICA_BASE_URL=https://your-instance.acumatica.com
ACUMATICA_USERNAME=your-username
ACUMATICA_PASSWORD=your-password
ACUMATICA_COMPANY=your-company
ACUMATICA_BRANCH=your-branch

# Odoo specific  
ODOO_BASE_URL=https://your-odoo-instance.com
ODOO_DATABASE=your-database
ODOO_USERNAME=your-username
ODOO_PASSWORD=your-password
```

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


