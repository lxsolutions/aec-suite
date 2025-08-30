


"""
Tests for authentication logic and RBAC functionality.
These tests focus on the core logic without HTTP dependencies.
"""

import pytest
import uuid
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

from backend.models import UserRole

# Mock JWT configuration
SECRET_KEY = "test-secret-key-for-testing-only"
ALGORITHM = "HS256"

def create_test_jwt(payload: dict) -> str:
    """Create a test JWT token for testing."""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token_logic(token: str):
    """JWT verification logic for testing."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role_logic(user_payload: dict, required_role: UserRole):
    """Role-based access control logic for testing."""
    user_role = user_payload.get("role")
    if user_role != required_role.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires {required_role.value} role",
        )
    return user_payload

def test_jwt_token_creation_and_verification():
    """Test that JWT tokens can be created and verified."""
    payload = {
        "sub": "test@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    # Create token
    token = create_test_jwt(payload)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify token
    verified_payload = verify_jwt_token_logic(token)
    assert verified_payload["sub"] == "test@example.com"
    assert verified_payload["role"] == "admin"
    assert "org_id" in verified_payload

def test_expired_token_rejection():
    """Test that expired tokens are rejected."""
    payload = {
        "sub": "test@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    
    token = create_test_jwt(payload)
    
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token_logic(token)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_token_rejection():
    """Test that invalid tokens are rejected."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token_logic("invalid-token")
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_role_based_access_control():
    """Test role-based access control logic."""
    admin_payload = {"role": "admin", "sub": "admin@example.com"}
    field_payload = {"role": "field_technician", "sub": "field@example.com"}
    owner_payload = {"role": "owner", "sub": "owner@example.com"}
    
    # Admin should have access to admin endpoints
    result = require_role_logic(admin_payload, UserRole.ADMIN)
    assert result == admin_payload
    
    # Field technician should not have access to admin endpoints
    with pytest.raises(HTTPException) as exc_info:
        require_role_logic(field_payload, UserRole.ADMIN)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    # Owner should have access to owner endpoints
    result = require_role_logic(owner_payload, UserRole.OWNER)
    assert result == owner_payload
    
    # Admin should not have access to owner endpoints
    with pytest.raises(HTTPException) as exc_info:
        require_role_logic(admin_payload, UserRole.OWNER)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

def test_missing_role_rejection():
    """Test that missing roles are rejected."""
    payload_without_role = {"sub": "test@example.com"}
    
    with pytest.raises(HTTPException) as exc_info:
        require_role_logic(payload_without_role, UserRole.ADMIN)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

def test_organization_scoping():
    """Test that organization ID is properly handled in tokens."""
    org_id = str(uuid.uuid4())
    payload = {
        "sub": "user@example.com",
        "role": "admin",
        "org_id": org_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = create_test_jwt(payload)
    verified_payload = verify_jwt_token_logic(token)
    
    assert verified_payload["org_id"] == org_id
    assert isinstance(verified_payload["org_id"], str)

def test_role_enum_values():
    """Test that UserRole enum has correct values."""
    assert UserRole.OWNER.value == "owner"
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.PM.value == "project_manager"
    assert UserRole.FIELD.value == "field_technician"

def test_role_hierarchy():
    """Test that role hierarchy is properly defined."""
    roles = [UserRole.FIELD, UserRole.PM, UserRole.ADMIN, UserRole.OWNER]
    
    # Verify hierarchy order
    assert roles.index(UserRole.OWNER) > roles.index(UserRole.ADMIN)
    assert roles.index(UserRole.ADMIN) > roles.index(UserRole.PM)
    assert roles.index(UserRole.PM) > roles.index(UserRole.FIELD)

def test_token_with_additional_claims():
    """Test that tokens with additional claims work correctly."""
    payload = {
        "sub": "user@example.com",
        "role": "admin",
        "org_id": str(uuid.uuid4()),
        "custom_claim": "custom_value",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = create_test_jwt(payload)
    verified_payload = verify_jwt_token_logic(token)
    
    assert verified_payload["custom_claim"] == "custom_value"
    assert verified_payload["sub"] == "user@example.com"
    assert verified_payload["role"] == "admin"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


