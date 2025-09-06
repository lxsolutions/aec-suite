
"""
Tests for multi-tenant RBAC and authentication functionality
"""

import pytest
import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.gateway.core.config import settings
from services.gateway.core.security import create_access_token_with_roles, get_current_user
from libs.py.aec_shared.models import UserRole, UserContext

# Test application setup
app = FastAPI()

@app.get("/protected")
async def protected_route(user: UserContext = Depends(get_current_user)):
    return {"user_id": user.user_id, "org_id": user.org_id, "roles": [r.value for r in user.roles]}

@app.get("/admin-only")
async def admin_route(user: UserContext = Depends(get_current_user)):
    if not user.has_role(UserRole.ORG_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return {"message": "Admin access granted"}

@app.get("/project-management")
async def project_management_route(user: UserContext = Depends(get_current_user)):
    required_roles = [UserRole.PROJECT_MANAGER, UserRole.ORG_ADMIN]
    if not user.has_any_role(required_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project management access required")
    return {"message": "Project management access granted"}

client = TestClient(app)

def create_test_token(user_id: str, org_id: str, roles: list):
    """Create a test JWT token with the given claims"""
    return create_access_token_with_roles(
        data={"sub": user_id, "org_id": org_id},
        roles=roles,
        expires_delta=timedelta(minutes=30)
    )

def test_valid_token_with_roles():
    """Test that a valid token with roles is properly parsed"""
    token = create_test_token("user-123", "org-456", [UserRole.ESTIMATOR, UserRole.VIEWER])
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-123"
    assert data["org_id"] == "org-456"
    assert "estimator" in data["roles"]
    assert "viewer" in data["roles"]

def test_admin_access_granted():
    """Test that admin users can access admin routes"""
    token = create_test_token("admin-user", "org-456", [UserRole.ORG_ADMIN])
    
    response = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Admin access granted"

def test_admin_access_denied():
    """Test that non-admin users cannot access admin routes"""
    token = create_test_token("regular-user", "org-456", [UserRole.ESTIMATOR])
    
    response = client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

def test_project_manager_access_granted():
    """Test that project managers can access project management routes"""
    token = create_test_token("pm-user", "org-456", [UserRole.PROJECT_MANAGER])
    
    response = client.get("/project-management", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Project management access granted"

def test_admin_can_access_project_management():
    """Test that admins can also access project management routes"""
    token = create_test_token("admin-user", "org-456", [UserRole.ORG_ADMIN])
    
    response = client.get("/project-management", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Project management access granted"

def test_estimator_cannot_access_project_management():
    """Test that estimators cannot access project management routes"""
    token = create_test_token("estimator-user", "org-456", [UserRole.ESTIMATOR])
    
    response = client.get("/project-management", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Project management access required" in response.json()["detail"]

def test_missing_token():
    """Test that requests without tokens are rejected"""
    response = client.get("/protected")
    
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

def test_invalid_token():
    """Test that invalid tokens are rejected"""
    response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_expired_token():
    """Test that expired tokens are rejected"""
    # Create token with past expiration
    expired_token = create_access_token_with_roles(
        data={"sub": "user-123", "org_id": "org-456"},
        roles=[UserRole.VIEWER],
        expires_delta=timedelta(minutes=-5)  # Expired 5 minutes ago
    )
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {expired_token}"})
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_token_missing_required_claims():
    """Test that tokens missing required claims are rejected"""
    # Create token without org_id
    invalid_token = jwt.encode(
        {"sub": "user-123", "exp": datetime.utcnow() + timedelta(minutes=30)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {invalid_token}"})
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_user_context_role_checking():
    """Test UserContext role checking methods"""
    user = UserContext(
        user_id="test-user",
        org_id="test-org",
        roles=[UserRole.ESTIMATOR, UserRole.VIEWER]
    )
    
    assert user.has_role(UserRole.ESTIMATOR) == True
    assert user.has_role(UserRole.ORG_ADMIN) == False
    assert user.has_any_role([UserRole.ESTIMATOR, UserRole.PROJECT_MANAGER]) == True
    assert user.has_any_role([UserRole.ORG_ADMIN, UserRole.PROJECT_MANAGER]) == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
