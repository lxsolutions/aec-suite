
# BuildForge Cloud

A production-grade, BIM-aware, ERP-connected AEC SaaS that supports residential, hospitality, commercial, and mixed-use projects end-to-end.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+

### Development Setup

1. **Clone and setup environment:**
   ```bash
   git clone https://github.com/your-org/buildforge-cloud.git
   cd buildforge-cloud
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start development environment:**
   ```bash
   make dev-up
   ```

3. **Run demos:**
   ```bash
   make demo-rfp        # RFP→Lint→Estimate workflow
   make demo-procure    # Procurement workflow
   make demo-field      # Field QA workflow
   make demo-buildforge # Full S1-S3 demo
   ```

## 📁 Project Structure

```
buildforge-cloud/
├── apps/
│   ├── web/          # Next.js SaaS web application
│   └── field/        # React Native Expo field app
├── services/
│   ├── api/          # FastAPI core API
│   ├── bim/          # IfcOpenShell service + PDF plan parser
│   ├── workers/      # Async jobs (Celery/Arq)
│   ├── policy/       # Rules DSL engine
│   ├── telemetry/    # Events ingestion (ClickHouse)
│   └── gateway/      # API gateway
├── integrations/
│   ├── acumatica/    # GI/OData/Contract API integration
│   ├── odoo/         # XML-RPC/REST integration
│   ├── procore/      # Import/export integration
│   └── identity/     # OIDC/SAML, SCIM integration
├── data/
│   ├── spec_rules/   # Versioned rulepacks
│   ├── cost_templates/ # CSI/MasterFormat templates
│   ├── samples/      # Anonymized RFPs, plans, IFCs
│   └── seeds/        # Demo data
├── db/
│   ├── migrations/   # Alembic migrations
│   └── ddl/          # Schema SQL
├── docs/             # Documentation
├── infra/            # Infrastructure definitions
└── scripts/          # Utility scripts
```

## 🎯 Target Slices

### SLICE 1 - RFP → Spec-Lint → Estimate v1
- Upload RFP (PDF/text) → compliance matrix + submittal index
- Map to estimate lines via CSI templates → export PDF
- Rules DSL with deterministic checks + LLM fallback

### SLICE 2 - Long-Lead + Procurement
- Vendor management, RFQs, POs, shipments
- Warehouse to room/unit kitting
- QR/barcode labeling system

### SLICE 3 - Field QA + Submittals
- Offline-first mobile app for ITPs, inspections, punch
- Submittal log & package builder
- Punch burn-down board

## 🔌 Integrations

- **Acumatica**: GI packages, OData, Contract API
- **Odoo**: XML-RPC/REST, budget/PO sync
- **Procore**: Project/files import/export
- **Identity**: OIDC/SAML, SCIM provisioning

## 🛡️ Security & Compliance

- Apache-2.0 License
- RBAC/ABAC with org/project isolation
- OIDC-ready authentication
- ISO-19650 CDE naming conventions
- Signed audit events with hash-chain verification

## 📊 Observability

- OpenTelemetry tracing
- Structured JSON logs
- ClickHouse for event analytics
- Request ID correlation

## 🧪 Testing & Quality

- Unit test coverage ≥ 70% for core services
- Lighthouse performance score ≥ 80
- WCAG AA accessibility compliance
- GitHub Actions CI/CD pipeline

## 📚 Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture and data model
- [SECURITY.md](docs/SECURITY.md) - Security model and best practices
- [ISO-19650-CDE.md](docs/ISO-19650-CDE.md) - CDE naming conventions
- [PILOT.md](docs/PILOT.md) - Pilot deployment guide
- [ROADMAP.md](docs/ROADMAP.md) - Development roadmap

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- 📖 Check the documentation
- 🐛 Open an issue on GitHub
- 💬 Join our community discussions

---

**BuildForge Cloud** - Building better, together. 🏗️
