

# ISO 19650 CDE Implementation

## Overview

This document outlines BuildForge Cloud's implementation of ISO 19650 Common Data Environment (CDE) standards for information management in construction projects.

## 📁 CDE Structure

### Project Container Structure
```
{project_number}-{project_name}/
├── 01-WIP/                    # Work in Progress
│   ├── 01-Architecture/
│   ├── 02-Structural/
│   ├── 03-MEP/
│   └── 04-Civil/
├── 02-Shared/                 # Shared for Review
│   ├── 01-For-Information/
│   ├── 02-For-Comment/
│   └── 03-For-Approval/
├── 03-Published/              # Published Documents
│   ├── 01-Archived/
│   └── 02-Current/
└── 04-Archive/                # Project Archive
    └── {version}/
```

## 🏷️ Naming Convention

### File Naming Structure
```
{project_number}-{originator}-{volume_system}-{level}-{type}-{role}-{number}-{revision}.{extension}
```

### Naming Components

| Component | Description | Example |
|-----------|-------------|---------|
| `project_number` | Unique project identifier | `P2024-001` |
| `originator` | Organization creating the file | `ABC-Arch` |
| `volume_system` | Building/system designation | `B1` or `MEP` |
| `level` | Floor/level designation | `L01` or `ROOF` |
| `type` | Document type code | `DR` (Drawing) |
| `role` | Discipline/role code | `AR` (Architect) |
| `number` | Sequential document number | `001` |
| `revision` | Revision identifier | `P01` (Proposed) |
| `extension` | File format | `.pdf`, `.ifc` |

### Document Type Codes

| Code | Description |
|------|-------------|
| `DR` | Drawing |
| `SP` | Specification |
| `RP` | Report |
| `CL` | Calculation |
| `MD` | Model |
| `PL` | Plan |
| `SH` | Schedule |
| `CO` | Correspondence |

### Discipline/Role Codes

| Code | Discipline |
|------|-----------|
| `AR` | Architecture |
| `ST` | Structural |
| `ME` | Mechanical |
| `EL` | Electrical |
| `PL` | Plumbing |
| `CV` | Civil |
| `LS` | Landscape |
| `QS` | Quantity Surveying |

## 🔄 Revision Control

### Revision Codes

| Code | Status | Description |
|------|--------|-------------|
| `P01`, `P02`... | Proposed | Work in progress |
| `S01`, `S02`... | Shared | For review/comment |
| `A01`, `A02`... | Approved | Client approved |
| `C01`, `C02`... | Construction | Issued for construction |
| `AS` | As-built | Final as-built |

### Revision Workflow

1. **WIP Stage**: `P01` → `P02` → `P03`...
2. **Shared Stage**: `S01` → `S02` → `S03`...
3. **Approved Stage**: `A01` → `A02` → `A03`...
4. **Construction**: `C01` → `C02` → `C03`...
5. **As-built**: `AS` (final)

## 📊 Metadata Schema

### Core Metadata Fields

```yaml
project:
  number: string
  name: string
  stage: string  # RIBA/ISO stage

file:
  name: string
  type: string
  discipline: string
  revision: string
  status: string  # WIP, Shared, Published, Archived

originator:
  organization: string
  author: string
  date_created: datetime

review:
  status: string  # For Information, For Comment, For Approval
  due_date: datetime
  reviewers: array

approval:
  status: string  # Approved, Rejected, Pending
  approver: string
  date_approved: datetime
```

## 🚀 Implementation in BuildForge

### API Endpoints

```python
# CDE Management
POST /cde/projects/{project_id}/upload
GET  /cde/projects/{project_id}/files
POST /cde/projects/{project_id}/files/{file_id}/review
POST /cde/projects/{project_id}/files/{file_id}/approve

# Metadata Management
GET  /cde/projects/{project_id}/metadata
POST /cde/projects/{project_id}/metadata/search

# Revision Control
GET  /cde/projects/{project_id}/files/{file_id}/revisions
POST /cde/projects/{project_id}/files/{file_id}/revisions
```

### Database Schema

```sql
CREATE TABLE cde_files (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    discipline TEXT NOT NULL,
    revision TEXT NOT NULL,
    status TEXT NOT NULL,
    originator_org TEXT NOT NULL,
    originator_author TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE cde_revisions (
    id UUID PRIMARY KEY,
    file_id UUID REFERENCES cde_files(id),
    revision_code TEXT NOT NULL,
    status TEXT NOT NULL,
    comment TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE cde_approvals (
    id UUID PRIMARY KEY,
    revision_id UUID REFERENCES cde_revisions(id),
    status TEXT NOT NULL,  -- approved, rejected, pending
    approver UUID REFERENCES users(id),
    comment TEXT,
    approved_at TIMESTAMPTZ
);
```

## 🔍 Validation Rules

### File Name Validation
- Must match ISO 19650 naming convention
- All required components must be present
- No special characters except hyphens
- Maximum length: 255 characters

### Metadata Validation
- Required fields must be populated
- Date formats must be ISO 8601
- Status must be from predefined list
- Revision codes must follow sequence

## 📋 Compliance Checklist

### For Project Setup
- [ ] Project number assigned
- [ ] CDE structure created
- [ ] Team roles and permissions configured
- [ ] Naming convention documented
- [ ] Revision workflow established

### For File Upload
- [ ] File name validated against convention
- [ ] Metadata extracted and stored
- [ ] Appropriate CDE location selected
- [ ] Revision history updated

### For Review Process
- [ ] Reviewers notified
- [ ] Due dates set
- [ ] Comments tracked
- [ ] Status updated

### For Approval Process
- [ ] Approvers identified
- [ ] Approval criteria verified
- [ ] Audit trail maintained
- [ ] Final status updated

## 🛠️ Integration Points

### BIM Tools
- Autodesk BIM 360/ACC
- Revit add-in for direct upload
- IFC file validation and processing

### Document Management
- PDF metadata extraction
- Office document processing
- Image file handling

### ERP Systems
- Project number synchronization
- Document status updates
- Approval workflow integration

## 🎯 Best Practices

### Do's
- Use consistent naming from project start
- Maintain complete metadata
- Follow revision control procedures
- Regular CDE audits and cleanup

### Don'ts
- Don't use spaces in file names
- Don't skip revision steps
- Don't store files outside CDE structure
- Don't bypass approval workflows

## 📚 References

- [ISO 19650-1:2018](https://www.iso.org/standard/68078.html) - Concepts and principles
- [ISO 19650-2:2018](https://www.iso.org/standard/68080.html) - Delivery phase of assets
- [UK BIM Framework](https://www.ukbimframework.org/)
- [NBS National BIM Library](https://www.nationalbimlibrary.com/)

## 🆘 Support

For CDE implementation questions:
- Contact: cde-support@buildforge.cloud
- Documentation: [CDE Implementation Guide]
- Training: Available upon request

---

*Last updated: 2025-08-28*
*Version: 1.0*

