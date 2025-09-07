

# BuildForge Cloud Architecture

## System Overview

BuildForge Cloud is a microservices-based architecture designed for scalability, security, and extensibility in the AEC (Architecture, Engineering, and Construction) domain.

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Client Applications                           │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │   Web App   │  │  Field App  │  │      Integration Clients       │  │
│  │ (Next.js)   │  │ (React Native)│  │ (Acumatica, Odoo, Procore)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API Gateway (Optional)                          │
│                  ┌─────────────────────────────────────┐                │
│                  │          Request Routing            │                │
│                  │        Authentication/Authorization │                │
│                  │          Rate Limiting              │                │
│                  └─────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            Core Services                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    API      │  │    BIM      │  │   Workers   │  │   Policy    │    │
│  │ (FastAPI)   │  │ (IfcOpenShell)│ │ (Celery/Arq)│ │ (Rules DSL) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            Data Layer                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ PostgreSQL  │  │ ClickHouse  │  │   Redis     │  │   MinIO     │    │
│  │ (Operational)│ │ (Analytics) │  │ (Cache/Queue)│ │ (File Store)│    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Core Services

### 1. API Service (`services/api`)
- **Framework**: FastAPI with Python 3.10+
- **Responsibilities**:
  - RESTful API endpoints
  - Authentication & authorization
  - Request validation
  - Business logic orchestration
- **Key Features**:
  - OpenAPI documentation
  - Dependency injection
  - Background task support
  - Health checks

### 2. BIM Service (`services/bim`)
- **Technologies**: IfcOpenShell, PDF parsing libraries
- **Responsibilities**:
  - IFC file processing and validation
  - PDF plan parsing and extraction
  - Geometry operations
  - BIM data normalization

### 3. Workers Service (`services/workers`)
- **Framework**: Celery with Redis/RabbitMQ
- **Responsibilities**:
  - Async task processing
  - Background jobs
  - Scheduled tasks
  - Email notifications
  - File processing

### 4. Policy Service (`services/policy`)
- **Technology**: Custom Rules DSL (YAML) + LLM fallback
- **Responsibilities**:
  - Rule execution engine
  - Compliance checking
  - Specification validation
  - LLM integration with tool guarding

## 🗃️ Data Storage

### PostgreSQL (Operational Data)
- **Schema**: Normalized relational data
- **Entities**:
  - Organizations, Projects, Users
  - RFPs, Estimates, Compliance findings
  - Vendors, RFQs, POs, Shipments
  - ITPs, Inspections, Punch items
  - Rooms, Units, Kitting assignments

### ClickHouse (Analytics & Events)
- **Schema**: Wide-column event storage
- **Data**:
  - Application events (rfp_imported, po_issued, etc.)
  - Audit logs
  - Performance metrics
  - Business intelligence data

### Redis (Cache & Queue)
- **Usage**:
  - Session storage
  - Rate limiting
  - Task queue backend
  - Cache for frequent queries

## 🔌 Integration Patterns

### 1. ERP Integrations
- **Acumatica**: GI packages, OData API, Contract API
- **Odoo**: XML-RPC, REST API, data synchronization
- **Procore**: OAuth2, REST API, file import/export

### 2. Identity Providers
- **OIDC/SAML**: Enterprise authentication
- **SCIM**: User provisioning
- **Social Auth**: Google, Microsoft, etc.

### 3. File Processing
- **PDF**: Text extraction, compliance checking
- **IFC**: BIM data processing
- **Images**: OCR, document processing

## 🛡️ Security Architecture

### Authentication
- JWT-based authentication
- OIDC/SAML integration
- Multi-factor authentication support

### Authorization
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Project/org isolation
- Fine-grained permissions

### Data Protection
- Encryption at rest (TDE)
- Encryption in transit (TLS 1.3)
- Secure secret management
- Audit logging with hash-chain

## 📊 Observability

### Logging
- Structured JSON logs
- Correlation IDs
- Log levels (DEBUG, INFO, WARN, ERROR)

### Metrics
- Prometheus metrics endpoint
- Custom business metrics
- Performance indicators

### Tracing
- OpenTelemetry integration
- Distributed tracing
- Performance analysis

## 🚀 Deployment

### Development
- Docker Compose for local development
- Hot reload for rapid iteration
- Sample data seeding

### Production
- Kubernetes deployment
- Horizontal pod autoscaling
- Database replication
- CDN for static assets

## 🔄 CI/CD Pipeline

### GitHub Actions
- **Linting**: Code quality checks
- **Testing**: Unit, integration, E2E tests
- **Security**: Vulnerability scanning
- **Deployment**: Staging and production

### Quality Gates
- Test coverage ≥ 70%
- Lighthouse score ≥ 80
- Accessibility compliance
- Security scanning passed

## 📈 Scaling Considerations

### Horizontal Scaling
- Stateless API services
- Read replicas for databases
- CDN for static assets
- Load balancing

### Vertical Scaling
- Database performance tuning
- Cache optimization
- Query optimization

## 🎨 Frontend Architecture

### Web App (`apps/web`)
- **Framework**: Next.js 14+
- **State Management**: Zustand + React Query
- **Styling**: Tailwind CSS + custom components
- **Features**: SSR, ISR, API routes

### Field App (`apps/field`)
- **Framework**: React Native Expo
- **State Management**: Zustand + Async Storage
- **Offline Support**: SQLite + sync engine
- **Features**: Camera, QR scanning, offline maps

## 🔮 Future Extensions

### Machine Learning
- Predictive analytics
- Anomaly detection
- Natural language processing

### Blockchain
- Smart contracts for payments
- Immutable audit trails
- Supply chain tracking

### IoT Integration
- Sensor data integration
- Equipment monitoring
- Environmental monitoring

---

*Last updated: 2025-08-28*
