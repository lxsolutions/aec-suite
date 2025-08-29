# BuildForge Cloud - Makefile
.PHONY: help dev-up dev-down demo-rfp demo-procure demo-field demo-resi demo-buildforge

help:
	@echo "BuildForge Cloud Development Commands"
	@echo "  dev-up          - Start development environment"
	@echo "  dev-down        - Stop development environment"
	@echo "  demo-rfp        - Run RFP→Lint→Estimate demo"
	@echo "  demo-procure    - Run procurement demo"
	@echo "  demo-field      - Run field QA demo"
	@echo "  demo-resi       - Run residential demo"
	@echo "  demo-buildforge - Run full S1-S3 demo"

dev-up:
	@echo "Starting development environment..."
	docker-compose -f infra/docker-compose.yml up -d

dev-down:
	@echo "Stopping development environment..."
	docker-compose -f infra/docker-compose.yml down

demo-rfp:
	@echo "Running RFP→Lint→Estimate demo..."
	@echo "TODO: Implement RFP demo script"

demo-procure:
	@echo "Running procurement demo..."
	@echo "TODO: Implement procurement demo script"

demo-field:
	@echo "Running field QA demo..."
	@echo "TODO: Implement field demo script"

demo-resi:
	@echo "Running residential demo..."
	@echo "TODO: Implement residential demo script"

demo-buildforge:
	@echo "Running full BuildForge demo (S1-S3)..."
	@echo "TODO: Implement full demo script chain"
