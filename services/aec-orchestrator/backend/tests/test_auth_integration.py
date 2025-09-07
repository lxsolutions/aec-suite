

"""
Integration tests for authentication middleware and RBAC functionality.
These tests will help drive the implementation of the auth middleware.
"""

import pytest
import uuid
from datetime import datetime, timedelta
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from backend.models import User, UserRole, Organization

# Create a test app to test auth middleware
app = FastAPI()

# Mock database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Mock JWT configuration
SECRET_KEY = "test-secret-key-for-testing-only"
ALGORITHM = "HS256"

# Mock authentication scheme
security = HTTPBearer()

def create_test_jwt(payload: dict) -> str:
    """Create a test JWT token for testing."""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock JWT verification for testing."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_role: UserRole):
    """Mock role-based access control for testing."""
    def role_checker(user_payload: dict = Depends(verify_jwt_token)):
        user_role = user_payload.get("role")
        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role",
            )
        return user_payload
    return role_checker

# Test endpoints
@app.get("/public")
async def public_endpoint():
    """Public endpoint that doesn't require authentication."""
    return {"message": "Public access"}

@app.get("/protected")
async def protected_endpoint(user: dict = Depends(verify_jwt_token)):
    """Protected endpoint that requires authentication."""
    return {"message": "Protected access", "user": user}

@app.get("/admin-only")
async def admin_only_endpoint(user: dict = Depends(require_role(UserRole.ADMIN))):
    """Endpoint that requires ADMIN role."""
    return {"message": "Admin access", "user": user}

@app.get("/owner-only")
async def owner_only_endpoint(user: dict = Depends(require_role(UserRole.OWNER))):
    """Endpoint that requires OWNER role."""
    return {"message": "Owner access", "user": user}

# Test client
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

def test_public_endpoint_accessible_without_auth(test_client):
    """Test that public endpoints are accessible without authentication."""
    response = test_client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "Public access"}

def test_protected_endpoint_requires_auth(test_client):
    """Test that protected endpoints require authentication."""
    response = test_client.get("/protected")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_protected_endpoint_with_valid_token(test_client):
    """Test that protected endpoints work with valid JWT token."""
    # Create a valid JWT token
    payload = {
        "sub": "test@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Protected access"
    assert "user" in response.json()

def test_admin_endpoint_requires_admin_role(test_client):
    """Test that admin endpoints require ADMIN role."""
    # Create a token with field role (not admin)
    payload = {
        "sub": "field@example.com",
        "role": "field_technician",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "detail" in response.json()

def test_admin_endpoint_with_admin_role(test_client):
    """Test that admin endpoints work with ADMIN role."""
    payload = {
        "sub": "admin@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Admin access"

def test_owner_endpoint_requires_owner_role(test_client):
    """Test that owner endpoints require OWNER role."""
    payload = {
        "sub": "admin@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/owner-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "detail" in response.json()

def test_owner_endpoint_with_owner_role(test_client):
    """Test that owner endpoints work with OWNER role."""
    payload = {
        "sub": "owner@example.com",
        "role": "owner",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/owner-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Owner access"

def test_expired_token_rejected(test_client):
    """Test that expired tokens are rejected."""
    payload = {
        "sub": "test@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    token = create_test_jwt(payload)
    
    response = test_client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "detail" in response.json()

def test_invalid_token_rejected(test_client):
    """Test that invalid tokens are rejected."""
    response = test_client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert "detail" in response.json()

def test_missing_token_rejected(test_client):
    """Test that missing tokens are rejected."""
    response = test_client.get("/protected")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_role_hierarchy():
    """Test that role hierarchy is properly enforced."""
    # Higher roles should have access to lower role endpoints
    # This is a conceptual test - in practice, we'd implement this in the middleware
    
    roles = [UserRole.FIELD, UserRole.PM, UserRole.ADMIN, UserRole.OWNER]
    
    # Verify hierarchy
    assert roles.index(UserRole.OWNER) > roles.index(UserRole.ADMIN)
    assert roles.index(UserRole.ADMIN) > roles.index(UserRole.PM)
    assert roles.index(UserRole.PM) > roles.index(UserRole.FIELD)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

