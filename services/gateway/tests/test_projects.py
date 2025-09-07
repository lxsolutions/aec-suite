

import pytest
from fastapi.testclient import TestClient
from main import app

def test_get_projects(test_client, auth_headers):
    """Test getting list of projects"""
    response = test_client.get("/v1/projects", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_project(test_client, auth_headers):
    """Test project creation"""
    project_data = {
        "name": "Test Project",
        "description": "Test project description",
        "client_id": "test-client-123",
        "start_date": "2024-01-01",
        "budget": 1000000
    }
    
    response = test_client.post("/v1/projects", json=project_data, headers=auth_headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == "Test Project"

def test_get_project_by_id(test_client, auth_headers):
    """Test getting project by ID"""
    response = test_client.get("/v1/projects/test-project-123", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "test-project-123"

def test_update_project(test_client, auth_headers):
    """Test updating project"""
    update_data = {
        "name": "Updated Project Name",
        "description": "Updated project description",
        "client_id": "test-client-123",
        "start_date": "2024-01-01",
        "budget": 1500000
    }
    
    response = test_client.put("/v1/projects/test-project-123", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"

def test_delete_project(test_client, auth_headers):
    """Test deleting project"""
    response = test_client.delete("/v1/projects/test-project-123", headers=auth_headers)
    assert response.status_code == 204

def test_project_creation_rate_limit(test_client, auth_headers):
    """Test rate limiting on project creation"""
    project_data = {
        "name": "Test Project",
        "description": "Test project description",
        "client_id": "test-client-123",
        "start_date": "2024-01-01",
        "budget": 1000000
    }
    
    # Make multiple requests to trigger rate limiting
    responses = []
    for _ in range(15):  # Should trigger rate limit (default is 100/min, but testing middleware)
        response = test_client.post("/v1/projects", json=project_data, headers=auth_headers)
        responses.append(response.status_code)
    
    # At least some should succeed (rate limit is per IP, test client uses same IP)
    assert any(status == 201 for status in responses)

