

"""
Simple test for RBAC functionality without pytest dependencies
"""

import sys
import os
from datetime import datetime, timedelta
from jose import jwt

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from services.gateway.core.config import settings
from services.gateway.core.security import create_access_token_with_roles
from libs.py.aec_shared.models import UserRole, UserContext

def test_token_creation():
    """Test that we can create tokens with roles"""
    print("Testing token creation with roles...")
    
    token = create_access_token_with_roles(
        data={"sub": "test-user", "org_id": "test-org"},
        roles=[UserRole.ESTIMATOR, UserRole.VIEWER],
        expires_delta=timedelta(minutes=30)
    )
    
    print(f"✓ Token created successfully: {token[:50]}...")
    
    # Verify the token can be decoded
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test-user"
    assert payload["org_id"] == "test-org"
    assert "estimator" in payload["roles"]
    assert "viewer" in payload["roles"]
    print("✓ Token payload contains correct claims")

def test_user_context():
    """Test UserContext role checking"""
    print("\nTesting UserContext role checking...")
    
    user = UserContext(
        user_id="test-user",
        org_id="test-org",
        roles=[UserRole.ESTIMATOR, UserRole.VIEWER]
    )
    
    # Test role checking
    assert user.has_role(UserRole.ESTIMATOR) == True
    assert user.has_role(UserRole.ORG_ADMIN) == False
    assert user.has_any_role([UserRole.ESTIMATOR, UserRole.PROJECT_MANAGER]) == True
    assert user.has_any_role([UserRole.ORG_ADMIN, UserRole.PROJECT_MANAGER]) == False
    
    print("✓ UserContext role checking works correctly")

def test_security_functions():
    """Test security utility functions"""
    print("\nTesting security utility functions...")
    
    # Test the original create_access_token still works
    from services.gateway.core.security import create_access_token
    token = create_access_token({"sub": "test-user", "org_id": "test-org"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test-user"
    assert payload["org_id"] == "test-org"
    print("✓ Original create_access_token function works")
    
    # Test the new create_access_token_with_roles
    token = create_access_token_with_roles(
        {"sub": "test-user", "org_id": "test-org"},
        [UserRole.ORG_ADMIN]
    )
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "org_admin" in payload["roles"]
    print("✓ create_access_token_with_roles function works")

if __name__ == "__main__":
    try:
        test_token_creation()
        test_user_context()
        test_security_functions()
        print("\n🎉 All RBAC tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

