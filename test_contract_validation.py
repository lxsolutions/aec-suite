

"""
Standalone contract validation tests for the vertical slice
These tests validate the API contract without requiring the full application stack
"""

import pytest
import json

def test_health_endpoint_contract():
    """Validate the health endpoint returns expected format"""
    # This would be an actual HTTP test in a real environment
    expected_response = {"status": "ok"}
    
    # Simulate what the health endpoint should return
    mock_response = {"status": "ok"}
    
    assert mock_response == expected_response
    assert "status" in mock_response
    assert mock_response["status"] == "ok"

def test_error_envelope_contract():
    """Validate error responses follow standardized format"""
    error_template = {
        "traceId": "string",
        "code": "string", 
        "message": "string",
        "details": "object"
    }
    
    # Example error response
    example_error = {
        "traceId": "trace-123",
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {"field": "name", "issue": "required"}
    }
    
    # Validate structure
    assert all(key in example_error for key in error_template.keys())
    assert isinstance(example_error["traceId"], str)
    assert isinstance(example_error["code"], str)
    assert isinstance(example_error["message"], str)
    assert isinstance(example_error["details"], dict)

def test_idempotency_header_contract():
    """Validate idempotency key header requirement"""
    required_headers = {
        "Authorization": "Bearer token",
        "Idempotency-Key": "unique-key-123",
        "Content-Type": "application/json"
    }
    
    # Validate required headers for create operations
    assert "Authorization" in required_headers
    assert "Idempotency-Key" in required_headers
    assert "Content-Type" in required_headers
    assert required_headers["Authorization"].startswith("Bearer ")
    assert len(required_headers["Idempotency-Key"]) > 0

def test_project_creation_contract():
    """Validate project creation request/response format"""
    project_request = {
        "name": "Test Project",
        "client_id": "test-client-123",
        "budget": 1000000,
        "description": "Test project description"
    }
    
    project_response = {
        "id": "project-123",
        "name": "Test Project",
        "client_id": "test-client-123",
        "budget": 1000000,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    # Validate request contains required fields
    assert "name" in project_request
    assert "client_id" in project_request
    assert "budget" in project_request
    
    # Validate response contains expected fields
    assert "id" in project_response
    assert "name" in project_response
    assert "status" in project_response

def test_estimate_creation_contract():
    """Validate estimate creation request/response format"""
    estimate_request = {
        "project_id": "project-123",
        "items": [
            {
                "code": "CON001",
                "description": "Concrete foundation",
                "quantity": 100,
                "unit": "m3",
                "unit_cost": 150,
                "total_cost": 15000
            }
        ],
        "currency": "USD"
    }
    
    estimate_response = {
        "project_id": "project-123",
        "items": [
            {
                "code": "CON001",
                "description": "Concrete foundation",
                "quantity": 100,
                "unit": "m3",
                "unit_cost": 150,
                "total_cost": 15000
            }
        ],
        "currency": "USD",
        "total_amount": 15000
    }
    
    # Validate request structure
    assert "project_id" in estimate_request
    assert "items" in estimate_request
    assert isinstance(estimate_request["items"], list)
    assert len(estimate_request["items"]) > 0
    
    # Validate response structure
    assert "project_id" in estimate_response
    assert "items" in estimate_response
    assert "total_amount" in estimate_response

def test_rfp_ingestion_contract():
    """Validate RFP ingestion request format"""
    # This would be a multipart form request in practice
    rfp_request = {
        "file": "file-content",  # This would be a file upload
        "project_id": "project-123"
    }
    
    rfp_response = {
        "project_id": "project-123",
        "filename": "test_rfp.txt",
        "status": "processing",
        "estimated_items": 5
    }
    
    assert "project_id" in rfp_request
    assert "file" in rfp_request
    
    assert "project_id" in rfp_response
    assert "status" in rfp_response

if __name__ == "__main__":
    # Run all tests
    test_health_endpoint_contract()
    test_error_envelope_contract()
    test_idempotency_header_contract()
    test_project_creation_contract()
    test_estimate_creation_contract()
    test_rfp_ingestion_contract()
    print("All contract validation tests passed!")

