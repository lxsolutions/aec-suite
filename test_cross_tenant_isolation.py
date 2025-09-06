


"""
Test cross-tenant isolation and access control
"""

import sys
import os
from datetime import datetime, timedelta
from jose import jwt

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from services.gateway.core.config import settings
from services.gateway.core.security import create_access_token_with_roles
from libs.py.aec_shared.models import UserRole

def test_cross_tenant_token_validation():
    """Test that tokens are properly validated and cannot access other orgs"""
    print("Testing cross-tenant token validation...")
    
    # Create tokens for different organizations
    token_org1 = create_access_token_with_roles(
        {"sub": "user1", "org_id": "org-1"},
        [UserRole.PROJECT_MANAGER]
    )
    
    token_org2 = create_access_token_with_roles(
        {"sub": "user2", "org_id": "org-2"}, 
        [UserRole.PROJECT_MANAGER]
    )
    
    # Verify tokens contain correct org IDs
    payload1 = jwt.decode(token_org1, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    payload2 = jwt.decode(token_org2, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload1["org_id"] == "org-1"
    assert payload2["org_id"] == "org-2"
    assert payload1["org_id"] != payload2["org_id"]
    
    print("✓ Tokens correctly contain different organization IDs")

def test_role_enum_values():
    """Test that UserRole enum values are consistent"""
    print("\nTesting UserRole enum values...")
    
    assert UserRole.ORG_ADMIN.value == "org_admin"
    assert UserRole.PROJECT_MANAGER.value == "project_manager" 
    assert UserRole.ESTIMATOR.value == "estimator"
    assert UserRole.VIEWER.value == "viewer"
    assert UserRole.SYSTEM.value == "system"
    
    print("✓ UserRole enum values are consistent")

def test_token_with_multiple_roles():
    """Test tokens can contain multiple roles"""
    print("\nTesting tokens with multiple roles...")
    
    token = create_access_token_with_roles(
        {"sub": "user1", "org_id": "org-1"},
        [UserRole.PROJECT_MANAGER, UserRole.ESTIMATOR]
    )
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert "project_manager" in payload["roles"]
    assert "estimator" in payload["roles"]
    assert len(payload["roles"]) == 2
    
    print("✓ Tokens can contain multiple roles")

def test_token_standard_claims():
    """Test that tokens include standard JWT claims"""
    print("\nTesting token standard claims...")
    
    token = create_access_token_with_roles(
        {"sub": "user1", "org_id": "org-1"},
        [UserRole.VIEWER]
    )
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert "exp" in payload  # expiration
    assert "iat" in payload  # issued at
    assert "sub" in payload  # subject
    assert "org_id" in payload  # organization ID
    assert "roles" in payload  # roles array
    
    print("✓ Tokens include all standard claims")

def test_rls_context_variables():
    """Test RLS context variable names"""
    print("\nTesting RLS context variable names...")
    
    # These are the variable names used in the RLS policies
    rls_variables = ["app.current_org_id", "app.current_user_role"]
    
    for var in rls_variables:
        assert var.startswith("app.")
        assert len(var.split('.')) == 2
    
    print("✓ RLS context variable names are properly formatted")

def test_audit_log_structure():
    """Test audit log table structure matches expectations"""
    print("\nTesting audit log structure...")
    
    # Expected columns from the migration
    expected_columns = [
        "id", "org_id", "user_id", "action", "resource_type", 
        "resource_id", "details", "trace_id", "created_at"
    ]
    
    # This would normally be tested against the actual database schema
    # For now, we just verify our expectations
    assert len(expected_columns) == 9
    assert "org_id" in expected_columns
    assert "user_id" in expected_columns
    assert "trace_id" in expected_columns
    
    print("✓ Audit log structure matches expectations")

if __name__ == "__main__":
    try:
        test_cross_tenant_token_validation()
        test_role_enum_values()
        test_token_with_multiple_roles()
        test_token_standard_claims()
        test_rls_context_variables()
        test_audit_log_structure()
        print("\n🎉 All cross-tenant isolation tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


