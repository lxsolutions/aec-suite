
# ADR 0004: Multi-tenant RBAC Implementation

## Status

Proposed

## Context

The AEC Suite needs to support multiple organizations (tenants) with proper isolation and role-based access control. Current authentication uses JWT tokens but lacks standardized tenant context and role enforcement.

Requirements:
- Support multiple organizations with data isolation
- Role-based access control (RBAC) for different user types
- Tenant context propagation across all services
- Audit logging with tenant context
- Cross-tenant access prevention

## Decision

### JWT Token Standardization

All JWT tokens will follow this standardized schema:

```json
{
  "sub": "user-123",           // User ID (subject)
  "org_id": "org-456",         // Organization ID
  "roles": ["admin", "user"],  // User roles
  "exp": 1735689600,           // Expiration timestamp
  "iat": 1735689000,           // Issued at timestamp
  "jti": "token-789"           // Token ID (for revocation)
}
```

### Role Definitions

Standard roles for multi-tenant RBAC:

1. **org_admin**: Full access to organization resources, user management
2. **project_manager**: Create/manage projects, estimates, RFPs
3. **estimator**: Create/view estimates, limited project access  
4. **viewer**: Read-only access to authorized resources
5. **system**: Internal service accounts (no tenant context)

### Tenant Isolation Strategies

1. **Database Level**: PostgreSQL Row Level Security (RLS) for tenant data isolation
2. **Application Level**: Query filtering by `org_id` in all data access operations
3. **Service Level**: Tenant context propagation via headers and JWT claims

### Implementation Requirements

1. **Gateway Policy Middleware**: 
   - Validate JWT tokens and extract tenant context
   - Enforce role-based access to API endpoints
   - Propagate tenant context to downstream services

2. **Database RLS Policies**:
   - Enable RLS on all tenant-scoped tables
   - Create policies that restrict access by `org_id`
   - System roles bypass RLS for cross-tenant operations

3. **Audit Logging**:
   - All audit logs must include `org_id`, `user_id`, `action`, `resource_id`
   - Include OpenTelemetry `trace_id` for correlation
   - Log all authentication and authorization events

4. **Service Communication**:
   - Propagate `X-Org-ID` header for internal service calls
   - Services must validate tenant context matches JWT claims
   - Fallback to header-based org context for service-to-service calls

## Consequences

### Positive
- Strong tenant isolation and data security
- Flexible role-based access control
- Comprehensive audit trail for compliance
- Scalable multi-tenant architecture

### Negative
- Increased complexity in database queries
- Performance overhead from RLS policies
- Additional validation logic in all services
- Migration effort for existing data models

### Risks
- RLS policy misconfiguration leading to data leaks
- Token validation failures breaking service communication
- Performance degradation under high tenant load
- Complex debugging of cross-tenant issues

## Migration Plan

1. **Phase 1**: Standardize JWT schema and update token generation
2. **Phase 2**: Implement gateway policy middleware with role checks
3. **Phase 3**: Add RLS policies to existing database tables
4. **Phase 4**: Update all services to handle tenant context propagation
5. **Phase 5**: Implement comprehensive audit logging
6. **Phase 6**: Create tests for cross-tenant access prevention

## Alternatives Considered

### Schema-per-Tenant
- **Pros**: Strongest isolation, better performance per tenant
- **Cons**: Complex migration, harder schema changes, more database connections

### Application-level Filtering Only  
- **Pros**: Simpler implementation, no database changes
- **Cons**: Weaker security, potential for query mistakes, no defense in depth

### Separate Database per Tenant
- **Pros**: Maximum isolation, dedicated resources
- **Cons**: Operational complexity, higher costs, difficult cross-tenant reporting

## References
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [NIST RBAC Guidelines](https://csrc.nist.gov/projects/role-based-access-control)
