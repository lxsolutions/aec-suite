


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
from main import app

client = TestClient(app, headers={'host': 'localhost'})

# Mock JWT token for authenticated tests
MOCK_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"

@pytest.fixture
def mock_nats():
    """Mock NATS connection"""
    with patch('core.events.nats.connect') as mock_connect:
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        yield mock_nc

def test_nats_connection_on_startup(mock_nats):
    """Test NATS connection during application startup"""
    # This test ensures NATS connection is attempted during app startup
    assert mock_nats.called

def test_publish_rfp_parsed_event():
    """Test publishing RFP parsed event to NATS"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.rfps.nats_client.publish') as mock_publish:
        mock_publish.return_value = AsyncMock()
        
        # Mock the orchestrator call
        with patch('api.v1.rfps.httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 202
            mock_post.return_value.json.return_value = {
                "message": "RFP processing started",
                "rfp_id": "rfp-test-789"
            }
            
            files = {
                "file": ("test_rfp.txt", "Test RFP content", "text/plain")
            }
            data = {"project_id": "test-project-123"}
            
            response = client.post("/v1/rfps/ingest", files=files, data=data, headers=headers)
            
            # Verify NATS publish was called
            assert mock_publish.called
            call_args = mock_publish.call_args
            assert call_args[0][0] == "rfp.parsed"  # Topic
            event_data = call_args[0][1]
            assert "rfp_id" in event_data
            assert "project_id" in event_data

def test_nats_event_structure():
    """Test NATS event structure and schema validation"""
    from libs.py.aec_shared.events import RfpParsedEvent
    
    # Test valid event creation
    event = RfpParsedEvent(
        rfp_id="test-rfp-123",
        project_id="test-project-456",
        filename="specifications.pdf",
        parsed_items=[
            {
                "code": "DIV01",
                "description": "Excavation",
                "quantity": 100.0,
                "unit": "cy"
            }
        ]
    )
    
    # Verify event can be serialized to JSON
    event_json = event.model_dump_json()
    event_dict = json.loads(event_json)
    
    assert event_dict["rfp_id"] == "test-rfp-123"
    assert event_dict["project_id"] == "test-project-456"
    assert len(event_dict["parsed_items"]) == 1

def test_nats_connection_failure_graceful():
    """Test graceful handling of NATS connection failure"""
    with patch('core.events.nats.connect', side_effect=Exception("Connection failed")):
        # Application should start even if NATS fails
        test_client = TestClient(app, headers={'host': 'localhost'})
        response = test_client.get("/v1/health")
        assert response.status_code == 200

def test_nats_publish_failure_graceful():
    """Test graceful handling of NATS publish failure"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.rfps.nats_client.publish', side_effect=Exception("Publish failed")):
        # Mock orchestrator call to succeed
        with patch('api.v1.rfps.httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 202
            mock_post.return_value.json.return_value = {
                "message": "RFP processing started",
                "rfp_id": "rfp-test-789"
            }
            
            files = {
                "file": ("test_rfp.txt", "Test RFP content", "text/plain")
            }
            data = {"project_id": "test-project-123"}
            
            # RFP ingestion should still succeed even if NATS publish fails
            response = client.post("/v1/rfps/ingest", files=files, data=data, headers=headers)
            assert response.status_code == 202


