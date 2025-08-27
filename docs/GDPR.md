








# GDPR Compliance Guide for AEC Orchestrator

This document outlines our commitment to General Data Protection Regulation (GDPR) compliance and data protection best practices.

## Data Minimization Principles

1. **Collection**: Only collect personal data that is necessary for project execution
2. **Storage**: Limit storage duration to what's required for business purposes
3. **Access**: Restrict access to personal data on a need-to-know basis

## User Rights Implementation

### Right to Access
Users can request copies of their personal data through the API:
```bash
curl -X GET "https://api.aec-orchestrator.com/users/me" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### Right to Erasure
Users can delete their accounts and associated data via:
```bash
curl -X DELETE "https://api.aec-orchestrator.com/users/me" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

## Data Anonymization

For analytics purposes, we implement the following anonymization strategies:

1. **Vector embeddings**: Store only mathematical vectors without personal identifiers
2. **Project data**: Remove PII before storing in knowledge base tables
3. **Audit logs**: Mask sensitive information in operational logs

## Security Measures

### Data Encryption
- **In transit**: All API endpoints use TLS 1.2+
- **At rest**: Database uses PostgreSQL's built-in encryption features

### Authentication
- JWT tokens with short expiration (15 minutes)
- Refresh tokens stored securely in HTTP-only cookies
- Password hashing using bcrypt with cost factor ≥ 10

## Data Retention Policies

| Data Type | Retention Period |
|-----------|------------------|
| User accounts | Until explicitly deleted by user or after 2 years of inactivity |
| Project data | 7 years (required for construction industry compliance) |
| Sensor logs | 3 months |
| Audit logs | 1 year |

## Compliance Monitoring

Regular security audits are performed to ensure:
- Proper implementation of access controls
- Effective monitoring of data processing activities
- Timely response to data subject requests




