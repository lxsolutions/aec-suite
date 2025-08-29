


"""
Test configuration for gateway service tests
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from main import app

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external service calls to avoid actual HTTP requests"""
    with patch('api.v1.projects.httpx.AsyncClient') as mock_client:
        # Mock successful responses for all external service calls
        mock_instance = AsyncMock()
        mock_instance.post.return_value.status_code = 201
        mock_instance.post.return_value.json.return_value = {
            "id": "test-project-123",
            "name": "Test Project",
            "client_id": "test-client-456",
            "status": "active"
        }
        mock_instance.get.return_value.status_code = 200
        mock_instance.get.return_value.json.return_value = {
            "id": "test-project-123",
            "name": "Test Project",
            "client_id": "test-client-456",
            "status": "active"
        }
        mock_instance.put.return_value.status_code = 200
        mock_instance.put.return_value.json.return_value = {
            "id": "test-project-123",
            "name": "Updated Project",
            "client_id": "test-client-456",
            "status": "active"
        }
        mock_instance.delete.return_value.status_code = 204
        
        mock_client.return_value = mock_instance
        yield

@pytest.fixture(autouse=True)  
def mock_nats_connection():
    """Mock NATS connection to avoid actual NATS server dependency"""
    with patch('core.events.nats.connect') as mock_connect:
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        yield mock_nc

@pytest.fixture
def test_client():
    """Test client fixture with proper headers"""
    return TestClient(app, headers={'host': 'localhost'})

@pytest.fixture
def auth_headers():
    """Authentication headers fixture"""
    return {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"}


