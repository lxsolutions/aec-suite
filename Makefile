.PHONY: bootstrap lint test build dev clean

# Default target
all: bootstrap

# Install all dependencies and tooling
bootstrap:
	@echo "Installing pnpm dependencies..."
	pnpm install
	@echo "Installing Python dependencies..."
	uv sync
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Bootstrap complete!"

# Run linting across all workspaces
lint:
	@echo "Running TypeScript linting..."
	pnpm run lint
	@echo "Running Python linting..."
	uv run ruff check .
	uv run black --check .
	@echo "Linting complete!"

# Run tests across all workspaces
test:
	@echo "Running TypeScript tests..."
	pnpm run test
	@echo "Running Python tests..."
	find . -name "pyproject.toml" -exec dirname {} \; | xargs -I {} sh -c "cd {} && uv run pytest --tb=short -v" \;
	@echo "Testing complete!"

# Build all packages and services
build:
	@echo "Building TypeScript packages..."
	pnpm run build
	@echo "Building Python packages..."
	find . -name "pyproject.toml" -exec dirname {} \; | xargs -I {} sh -c "cd {} && uv build" \;
	@echo "Build complete!"

# Start development environment
dev:
	@echo "Starting development services..."
	docker-compose up -d
	pnpm run dev

# Start only infrastructure services
dev.infra:
	@echo "Starting infrastructure services..."
	docker-compose up -d postgres redis nats jaeger

# Clean build artifacts and dependencies
clean:
	@echo "Cleaning build artifacts..."
	rm -rf node_modules
	rm -rf **/dist
	rm -rf **/build
	rm -rf **/.pytest_cache
	rm -rf **/__pycache__
	rm -rf **/*.egg-info
	@echo "Clean complete!"

# Show help
help:
	@echo "Available targets:"
	@echo "  bootstrap  - Install all dependencies and tooling"
	@echo "  lint       - Run linting across all workspaces"
	@echo "  test       - Run tests across all workspaces"
	@echo "  build      - Build all packages and services"
	@echo "  dev        - Start development environment"
	@echo "  dev.infra  - Start only infrastructure services"
	@echo "  clean      - Clean build artifacts and dependencies"
	@echo "  help       - Show this help message"

# Gateway specific targets
gateway.run:
	@echo "Starting Gateway service..."
	cd services/gateway && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8080

test.gateway:
	@echo "Running Gateway tests..."
	cd services/gateway && uv run pytest --tb=short -v

gateway.install:
	@echo "Installing Gateway dependencies..."
	cd services/gateway && uv pip install -e .
