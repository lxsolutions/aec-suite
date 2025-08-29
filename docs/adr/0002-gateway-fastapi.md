

# ADR 0002: FastAPI Gateway Implementation

## Status

Accepted

## Context

The AEC Suite requires a robust API gateway to handle authentication, rate limiting, request routing, and observability. The gateway was initially implemented using NestJS but faced several challenges:

- Complex TypeScript/Node.js dependency management
- Performance overhead for high-throughput API requests
- Limited Python ecosystem integration for data science and ML workflows
- Inconsistent development patterns across the polyglot codebase

## Decision

We will migrate the API gateway from NestJS to FastAPI with the following architecture:

### Core Components

1. **FastAPI Application**: Modern, high-performance Python web framework
2. **JWT Authentication**: HS256 signing with X-Org-ID header support
3. **Rate Limiting**: Per-IP and per-user rate limiting using slowapi
4. **OpenTelemetry**: Distributed tracing with Jaeger exporter
5. **NATS Integration**: Event publishing for cross-service communication
6. **Database Layer**: Async PostgreSQL connection with SQLAlchemy

### API Structure

```
/v1
├── /health          - Health checks with dependency status
├── /projects        - Project management CRUD operations
├── /rfps            - RFP ingestion and management
├── /estimates       - Estimate generation and retrieval
└── /readyz          - Kubernetes readiness probe
```

### Dependencies

```python
# Core dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
python-jose>=3.3.0
slowapi>=0.1.8
limits>=3.6.0

# Observability
opentelemetry-sdk>=1.19.0
opentelemetry-exporter-jaeger>=1.19.0
opentelemetry-instrumentation-fastapi>=0.11b0

# Messaging
nats-py>=2.0.0

# Database
asyncpg>=0.28.0
sqlalchemy>=2.0.0
```

## Consequences

### Positive

- **Performance**: FastAPI provides excellent performance with async/await support
- **Python Ecosystem**: Seamless integration with data science and ML libraries
- **Developer Experience**: Excellent documentation and intuitive API design
- **Type Safety**: Pydantic models provide runtime type validation
- **Async Support**: Native support for async database operations and external calls

### Negative

- **Migration Effort**: One-time cost to rewrite NestJS endpoints
- **Learning Curve**: Developers need to learn FastAPI patterns
- **Dependency Management**: Python dependency resolution can be complex

### Risks

- **Dependency Conflicts**: Potential version conflicts in Python ecosystem
- **Async Complexity**: Requires careful handling of async/await patterns
- **Monitoring**: Need to ensure OpenTelemetry integration works correctly

## Migration Plan

1. **Phase 1**: Set up FastAPI skeleton with health endpoints
2. **Phase 2**: Implement JWT authentication and dependency injection
3. **Phase 3**: Migrate project management endpoints
4. **Phase 4**: Implement RFP ingestion with file upload
5. **Phase 5**: Add estimate generation endpoints
6. **Phase 6**: Integrate NATS for event publishing
7. **Phase 7**: Add rate limiting and observability
8. **Phase 8**: Remove NestJS artifacts and update documentation

## Alternatives Considered

### NestJS (Current)

- **Pros**: TypeScript ecosystem, familiar to frontend developers
- **Cons**: Performance overhead, limited Python integration

### Go with Gin

- **Pros**: Excellent performance, strong concurrency model
- **Cons**: Steeper learning curve, less ecosystem maturity

### Django with Django REST Framework

- **Pros**: Batteries-included, excellent admin interface
- **Cons**: Synchronous by default, heavier framework

## Implementation Details

### Authentication

```python
# JWT decoding with HS256
def decode_jwt(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# Org ID extraction with fallback
def get_org_id(request: Request) -> str:
    return request.headers.get("X-Org-ID", "default-org")
```

### Rate Limiting

```python
# Global rate limit (100 requests/minute)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Per-endpoint limits
@app.post("/v1/projects")
@limiter.limit("10/minute")
async def create_project(...):
```

### Error Handling

```python
# Uniform error response
class ErrorResponse(BaseModel):
    traceId: str
    code: str
    message: str
    details: Optional[dict] = None
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [NATS.py Documentation](https://github.com/nats-io/nats.py)
- [SlowAPI Rate Limiting](https://github.com/laurentS/slowapi)

