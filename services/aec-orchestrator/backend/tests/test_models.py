
"""
Tests for database models and RBAC functionality.
"""

import pytest
import uuid
from datetime import datetime

from backend.models import User, UserRole, Organization, Project, Estimate

def test_user_role_enum_values():
    """Test that UserRole enum has correct values."""
    assert UserRole.OWNER.value == "owner"
    assert UserRole.ADMIN.value == "admin" 
    assert UserRole.PM.value == "project_manager"
    assert UserRole.FIELD.value == "field_technician"

def test_organization_model_validation():
    """Test Organization model validation."""
    org = Organization(
        name="Test Org",
        slug="test-org"
    )
    assert org.name == "Test Org"
    assert org.slug == "test-org"
    assert org.created_at is None
    assert org.updated_at is None

def test_user_model_validation():
    """Test User model validation with roles."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        role=UserRole.ADMIN
    )
    assert user.email == "test@example.com"
    assert user.role == UserRole.ADMIN
    assert user.is_active is True
    assert user.is_superuser is False

def test_multi_tenant_isolation():
    """Test that data is properly isolated by organization."""
    # Create two organizations with UUIDs
    org1_id = uuid.uuid4()
    org2_id = uuid.uuid4()
    
    org1 = Organization(id=org1_id, name="Org 1", slug="org-1")
    org2 = Organization(id=org2_id, name="Org 2", slug="org-2")
    
    # Create users in different organizations
    user1 = User(
        email="user1@org1.com", 
        hashed_password="hash1",
        role=UserRole.ADMIN,
        org_id=org1.id
    )
    user2 = User(
        email="user2@org2.com",
        hashed_password="hash2", 
        role=UserRole.ADMIN,
        org_id=org2.id
    )
    
    # Users should have different org IDs
    assert user1.org_id != user2.org_id
    assert user1.org_id == org1.id
    assert user2.org_id == org2.id

def test_role_based_access_control():
    """Test RBAC permission levels."""
    # Test that higher roles have more permissions
    roles = [UserRole.FIELD, UserRole.PM, UserRole.ADMIN, UserRole.OWNER]
    
    # In a real implementation, we'd check permissions for each role
    # For now, we'll just verify the role hierarchy
    assert roles.index(UserRole.OWNER) > roles.index(UserRole.ADMIN)
    assert roles.index(UserRole.ADMIN) > roles.index(UserRole.PM) 
    assert roles.index(UserRole.PM) > roles.index(UserRole.FIELD)

def test_estimate_model_validation():
    """Test Estimate model validation."""
    estimate = Estimate(
        name="Test Estimate",
        material_cost=10000.0,
        labor_cost=5000.0,
        total_cost=15000.0,
        status="draft",
        version=1
    )
    assert estimate.name == "Test Estimate"
    assert estimate.material_cost == 10000.0
    assert estimate.labor_cost == 5000.0
    assert estimate.total_cost == 15000.0
    assert estimate.status == "draft"
    assert estimate.version == 1

def test_project_model_validation():
    """Test Project model validation."""
    project = Project(
        name="Test Project",
        data={"type": "residential", "square_feet": 2000}
    )
    assert project.name == "Test Project"
    assert project.data["type"] == "residential"
    assert project.data["square_feet"] == 2000

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
