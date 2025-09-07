


"""
Test configuration for gateway service tests
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'libs', 'py'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', '..', 'libs', 'py'))
from main import app

@pytest.fixture
def test_client():
    """Test client fixture with proper headers"""
    return TestClient(app, headers={'host': 'localhost'})

@pytest.fixture
def auth_headers():
    """Authentication headers fixture"""
    # Create a valid JWT token using the correct secret key
    from jose import jwt
    from datetime import datetime, timedelta
    
    token_data = {
        "sub": "test-user",
        "org_id": "test-org",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_data, "change-me-in-production", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external service calls to avoid actual HTTP requests"""
    with patch('api.dependencies.httpx.AsyncClient') as mock_client:
        # Mock successful responses for all external service calls
        mock_instance = AsyncMock()
        
        # Mock the async context manager behavior
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        
        # Mock post response
        mock_post_response = Mock()
        mock_post_response.status_code = 201
        mock_post_response.json.return_value = {
            "id": "test-project-123",
            "name": "Test Project",
            "description": "Test project description",
            "client_id": "test-client-456",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "budget": 100000.0,
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_post_response.raise_for_status.return_value = None
        
        # Mock get response for list projects
        mock_get_list_response = Mock()
        mock_get_list_response.status_code = 200
        mock_get_list_response.json.return_value = [
            {
                "id": "test-project-123",
                "name": "Test Project",
                "description": "Test project description",
                "client_id": "test-client-456",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "budget": 100000.0,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_get_list_response.raise_for_status.return_value = None
        
        # Mock get response for single project
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": "test-project-123",
            "name": "Test Project",
            "description": "Test project description",
            "client_id": "test-client-456",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "budget": 100000.0,
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_get_response.raise_for_status.return_value = None
        
        # Mock put response
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {
            "id": "test-project-123",
            "name": "Updated Project",
            "description": "Updated project description",
            "client_id": "test-client-456",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "budget": 150000.0,
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
        mock_put_response.raise_for_status.return_value = None
        
        # Mock delete response
        mock_delete_response = Mock()
        mock_delete_response.status_code = 204
        mock_delete_response.raise_for_status.return_value = None
        
        # Mock different responses based on URL
        def mock_get_method(url, **kwargs):
            if "/projects" in url and not "/projects/" in url:
                # List projects endpoint
                return mock_get_list_response
            elif "/projects/" in url:
                # Single project endpoint
                return mock_get_response
            else:
                # Other endpoints - return error
                raise Exception(f"URL not mocked: {url}")
        
        def mock_post_method(url, **kwargs):
            if "/projects" in url:
                # Project endpoints - use the existing mock response
                return mock_post_response
            elif "/rfps/ingest" in url:
                # RFP ingest endpoint - return RFP response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "id": "rfp-test-789",
                    "project_id": "test-project-123",
                    "title": "Test RFP",
                    "description": "Test RFP description",
                    "due_date": "2024-12-31",
                    "budget_range_min": 50000.0,
                    "budget_range_max": 100000.0,
                    "requirements": ["Test requirement 1", "Test requirement 2"],
                    "status": "parsed",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
                mock_response.raise_for_status.return_value = None
                return mock_response
            else:
                # Other endpoints - return error
                raise Exception(f"URL not mocked: {url}")
        
        mock_instance.post.side_effect = mock_post_method
        mock_instance.get.side_effect = mock_get_method
        mock_instance.put.return_value = mock_put_response
        mock_instance.delete.return_value = mock_delete_response
        
        mock_client.return_value = mock_instance
        yield

@pytest.fixture(autouse=True)  
def mock_nats_connection():
    """Mock NATS connection to avoid actual NATS server dependency"""
    with patch('core.events.nats_client.connect') as mock_connect:
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        yield mock_nc


