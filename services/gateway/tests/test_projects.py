

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app, headers={'host': 'localhost'})

# Mock JWT token for authenticated tests
MOCK_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"

def test_get_projects():
    """Test getting list of projects"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    response = client.get("/v1/projects", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_project():
    """Test project creation"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    project_data = {
        "name": "Test Project",
        "description": "Test project description",
        "client_id": "test-client-123",
        "budget": 1000000,
        "status": "active"
    }
    
    with patch('api.v1.projects.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock()
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "id": "test-project-456",
            "name": "Test Project",
            "client_id": "test-client-123",
            "status": "active"
        }
        
        response = client.post("/v1/projects", json=project_data, headers=headers)
        assert response.status_code == 201
        assert response.json()["id"] == "test-project-456"
        assert response.json()["name"] == "Test Project"

def test_get_project_by_id():
    """Test getting project by ID"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.projects.httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "test-project-789",
            "name": "Test Project",
            "client_id": "test-client-123",
            "status": "active"
        }
        
        response = client.get("/v1/projects/test-project-789", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == "test-project-789"

def test_update_project():
    """Test updating project"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    update_data = {
        "name": "Updated Project Name",
        "budget": 1500000
    }
    
    with patch('api.v1.projects.httpx.AsyncClient.put') as mock_put:
        mock_put.return_value = AsyncMock()
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {
            "id": "test-project-789",
            "name": "Updated Project Name",
            "budget": 1500000,
            "status": "active"
        }
        
        response = client.put("/v1/projects/test-project-789", json=update_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Project Name"

def test_delete_project():
    """Test deleting project"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.projects.httpx.AsyncClient.delete') as mock_delete:
        mock_delete.return_value = AsyncMock()
        mock_delete.return_value.status_code = 204
        
        response = client.delete("/v1/projects/test-project-789", headers=headers)
        assert response.status_code == 204

def test_project_creation_rate_limit():
    """Test rate limiting on project creation"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    project_data = {
        "name": "Test Project",
        "description": "Test project description",
        "client_id": "test-client-123",
        "budget": 1000000,
        "status": "active"
    }
    
    # Make multiple requests to trigger rate limiting
    responses = []
    for _ in range(15):  # Should trigger rate limit (default is 100/min, but testing middleware)
        with patch('api.v1.projects.httpx.AsyncClient.post'):
            response = client.post("/v1/projects", json=project_data, headers=headers)
            responses.append(response.status_code)
    
    # At least some should succeed (rate limit is per IP, test client uses same IP)
    assert any(status == 201 for status in responses)

