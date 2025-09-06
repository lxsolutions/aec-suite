# ADR 0003: Error Model Standardization

## Status

Proposed

## Context

The AEC Suite currently has inconsistent error handling across services:
- Gateway uses `AECError` model but with field naming inconsistencies (`traceId` vs `trace_id`)
- Orchestrator uses basic `HTTPException` without standardized error envelope
- Services lack consistent HTTP status code usage
- No uniform error response format for clients

This inconsistency makes client integration difficult and reduces observability.

## Decision

We will standardize on a uniform error response format across all HTTP services:

### Error Response Format
```json
{
  "trace_id": "string (UUID)",
  "code": "string (machine-readable error code)",
  "message": "string (human-readable error message)", 
  "details": "object (optional additional context)"
}
```

### Field Definitions
- **trace_id**: OpenTelemetry trace ID for distributed tracing correlation
- **code**: Machine-readable error code (e.g., "validation_error", "not_found", "rate_limited")
- **message**: Human-readable error description
- **details**: Optional object with additional context (field validation errors, resource IDs, etc.)

### HTTP Status Code Mapping
- `400 Bad Request`: Validation errors, malformed requests
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Authenticated but insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (duplicate, concurrent modification)
- `429 Too Many Requests`: Rate limiting
- `500 Internal Server Error`: Unexpected server errors
- `503 Service Unavailable`: Dependent service unavailable

### Implementation Requirements
1. All HTTP services must use the `AECError` model from `libs/py/aec_shared/errors`
2. Error responses must include the current trace ID from OpenTelemetry context
3. Services must use appropriate HTTP status codes for error types
4. All create operations (POST/PUT) should support idempotency keys

## Consequences

### Positive
- Consistent client error handling experience
- Improved observability with trace ID correlation
- Better debugging and troubleshooting capabilities
- Standardized error codes for programmatic handling

### Negative
- One-time migration effort for existing services
- Additional overhead for error response formatting
- Need to ensure trace ID propagation across all services

### Risks
- Inconsistent implementation across services
- Performance impact from additional error processing
- Trace ID propagation failures breaking error correlation

## Migration Plan

1. **Phase 1**: Update gateway to use consistent `AECError` field names
2. **Phase 2**: Add error middleware to orchestrator service
3. **Phase 3**: Implement error handling in new services (erp-bridge, rover-estimate)
4. **Phase 4**: Add idempotency key support for create operations
5. **Phase 5**: Create comprehensive contract tests for error scenarios

## Alternatives Considered

### Custom Error Middleware per Service
- **Pros**: Service-specific error handling customization
- **Cons**: Inconsistency, duplication of effort, maintenance overhead

### Framework-specific Error Handling
- **Pros**: Leverages framework capabilities
- **Cons**: Framework lock-in, inconsistent across polyglot services

### No Standardization
- **Pros**: No migration effort
- **Cons**: Poor developer experience, difficult client integration, reduced observability

## References
- [RFC 7807: Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [Google JSON Style Guide: Error Format](https://google.github.io/styleguide/jsoncstyleguide.xml#Error_Format)
- [Microsoft REST API Guidelines: Error Response](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#error-response)
