


"""
Test configuration for gateway service tests
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../libs/py'))

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from main import app

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external service calls to avoid actual HTTP requests"""
    # Mock the get_service_health function directly
    with patch('api.v1.health.get_service_health') as mock_health:
        mock_health.return_value = {
            "orchestrator": {"status": "healthy", "status_code": 200},
            "rover": {"status": "healthy", "status_code": 200},
            "erp_bridge": {"status": "healthy", "status_code": 200},
            "buildforge": {"status": "healthy", "status_code": 200}
        }
        
        # Also mock httpx for other service calls
        with patch('api.dependencies.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value.status_code = 201
            mock_instance.post.return_value.json.return_value = {
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


