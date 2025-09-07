


# Pilot Deployment Guide

## Overview

This guide provides step-by-step instructions for running a BuildForge Cloud pilot on a live construction project.

## 🎯 Pilot Objectives

### Primary Goals
1. Validate end-to-end workflow from RFP to Handover
2. Test integration with existing ERP systems
3. Gather user feedback from all project roles
4. Measure time savings and error reduction
5. Assess scalability for full deployment

### Success Metrics
- **Process Efficiency**: 30% reduction in manual data entry
- **Error Reduction**: 50% fewer compliance issues
- **User Satisfaction**: 4/5 average rating from pilot team
- **Integration Success**: 95% successful data syncs

## 📋 Pre-Pilot Checklist

### Infrastructure Requirements
- [ ] Docker and Docker Compose installed
- [ ] 8GB RAM minimum, 16GB recommended
- [ ] 100GB storage for project data
- [ ] Stable internet connection
- [ ] Backup strategy in place

### Team Preparation
- [ ] Project executive sponsor identified
- [ ] Pilot team members trained
- [ ] Roles and permissions configured
- [ ] Support contacts established

### Data Preparation
- [ ] Sample RFP documents ready
- [ ] Vendor database exported
- [ ] Cost templates prepared
- [ ] Project structure defined

## 🚀 Pilot Deployment Steps

### Phase 1: Environment Setup (Day 1-2)

1. **Infrastructure Deployment**
   ```bash
   # Clone the repository
   git clone https://github.com/your-org/buildforge-cloud.git
   cd buildforge-cloud
   
   # Configure environment
   cp .env.example .env
   # Edit .env with project-specific settings
   
   # Start services
   make dev-up
   ```

2. **Database Initialization**
   ```bash
   # Run migrations
   docker-compose -f infra/docker-compose.yml exec api \
     alembic upgrade head
   
   # Seed demo data
   docker-compose -f infra/docker-compose.yml exec api \
     python -m scripts.seed_pilot_data
   ```

3. **User Onboarding**
   - Create user accounts for pilot team
   - Assign roles and permissions
   - Conduct training sessions

### Phase 2: Workflow Validation (Day 3-7)

#### RFP → Estimate Workflow
1. Upload 3-5 sample RFP documents
2. Run compliance checking (linting)
3. Review and validate findings
4. Generate initial estimates
5. Export reports for comparison

#### Procurement Workflow
1. Create vendor records
2. Generate RFQs for long-lead items
3. Process quotes and issue POs
4. Track shipments and receipts
5. Test kitting functionality

#### Field QA Workflow
1. Set up ITP templates
2. Conduct sample inspections
3. Create punch items with photos
4. Test offline functionality
5. Validate sync process

### Phase 3: Integration Testing (Day 8-10)

#### ERP Integration
```bash
# Test Acumatica integration
make test-acumatica

# Test Odoo integration  
make test-odoo

# Test Procore integration
make test-procore
```

#### Data Validation
- Compare system data with source systems
- Validate financial calculations
- Check data consistency across modules
- Test error handling and recovery

### Phase 4: Performance Monitoring (Day 11-14)

#### System Metrics
```bash
# Monitor performance
make monitor-performance

# Check error rates
make check-errors

# Generate usage reports
make usage-report
```

#### User Feedback
- Daily standup meetings
- Feedback surveys
- Issue tracking and resolution
- Success story collection

## 📊 Pilot Metrics Collection

### Quantitative Metrics
```sql
-- Process efficiency
SELECT COUNT(*) as manual_entries_before, COUNT(*) as manual_entries_after
FROM process_metrics WHERE pilot_phase = 'before' OR pilot_phase = 'after';

-- Error rates  
SELECT error_type, COUNT(*) as occurrences
FROM error_log WHERE timestamp > pilot_start_date
GROUP BY error_type;

-- User activity
SELECT user_role, COUNT(*) as actions, AVG(time_spent) as avg_time
FROM user_activity GROUP BY user_role;
```

### Qualitative Metrics
- User satisfaction surveys
- Feature usefulness ratings
- Improvement suggestions
- Pain point identification

## 🛠️ Troubleshooting Guide

### Common Issues

**Database Connection Issues**
```bash
# Check database status
docker-compose -f infra/docker-compose.yml logs postgres

# Test connection
docker-compose -f infra/docker-compose.yml exec api \
  python -c "import psycopg2; psycopg2.connect('postgresql://buildforge:buildforge@postgres:5432/buildforge')"
```

**File Upload Problems**
- Check file size limits
- Verify file permissions
- Review storage capacity

**Integration Failures**
- Check API credentials
- Verify network connectivity
- Review error logs

### Support Contacts

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| Technical Issues | DevOps Team | 2 hours |
| Functional Questions | Product Team | 4 hours |
| Emergency Outages | 24/7 Support | 30 minutes |

## 📝 Pilot Reporting

### Daily Reports
- System uptime and performance
- User activity summary
- Issues and resolutions
- Key learnings

### Weekly Summary
- Progress against objectives
- Metric trends
- Risk assessment
- Adjustment recommendations

### Final Report
- Executive summary
- Quantitative results
- Qualitative feedback
- Go/no-go recommendation
- Scaling plan

## 🔄 Pilot Extension Criteria

### Extend Pilot If:
- Additional use cases identified
- More data needed for validation
- Team requests more time
- Integration testing incomplete

### Conclude Pilot If:
- Success metrics achieved
- Major blocking issues unresolved
- Budget/time constraints reached
- Strategic direction changed

## 🎯 Post-Pilot Actions

### Successful Pilot
1. **Planning**: Develop full deployment plan
2. **Scaling**: Infrastructure capacity planning
3. **Training**: Expand user training programs
4. **Support**: Establish ongoing support model

### Unsuccessful Pilot
1. **Analysis**: Root cause analysis
2. **Improvement**: Address identified issues
3. **Re-evaluation**: Consider alternative approaches
4. **Documentation**: Lessons learned repository

## 📋 Pilot Acceptance Criteria

### Must Have
- [ ] All core workflows functional
- [ ] Data integrity maintained
- [ ] Performance requirements met
- [ ] User training completed

### Should Have  
- [ ] Key integrations working
- [ ] Positive user feedback
- [ />] Metric targets achieved
- [ ] Documentation updated

### Nice to Have
- [ ] Additional use cases validated
- [ ] Customizations implemented
- [ ] Advanced features tested
- [ ] Performance optimizations

## 🆘 Emergency Procedures

### Data Loss
1. Immediately stop all operations
2. Contact DevOps team
3. Restore from latest backup
4. Investigate root cause

### Security Incident
1. Isolate affected systems
2. Preserve evidence
3. Contact security team
4. Follow incident response plan

### System Outage
1. Notify all users
2. Begin troubleshooting
3. Provide status updates
4. Document resolution steps

---

*Last updated: 2025-08-28*
*Version: 1.0*

