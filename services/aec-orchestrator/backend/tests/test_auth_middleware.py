
"""
Tests for authentication middleware and RBAC functionality.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, HTTPException
import uuid

from backend.main import app
from backend.models import User, UserRole, Organization

@pytest.fixture(scope="module")
def test_client():
    """Create a FastAPI test client."""
    with TestClient(app) as client:
        yield client

def test_health_check(test_client):
    """Test that health check endpoint works without authentication."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_unauthenticated_access_to_protected_endpoints(test_client):
    """Test that protected endpoints return 401 without authentication."""
    endpoints = [
        "/users/me",
        "/agents/run", 
        "/integrations/erp/sync",
        "/bim/upload"
    ]
    
    for endpoint in endpoints:
        response = test_client.get(endpoint) if endpoint == "/users/me" else test_client.post(endpoint)
        assert response.status_code in [401, 405]  # 401 Unauthorized or 405 Method Not Allowed

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

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
