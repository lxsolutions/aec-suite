


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
from main import app

client = TestClient(app, headers={'host': 'localhost'})

# Mock JWT token for authenticated tests
MOCK_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NzIxNjE4MX0.jbL-8Sx9N-vJ97mhGIW1ivJmIZXlmAlWOHMCgTtxbvM"

@pytest.fixture
def mock_nats():
    """Mock NATS connection"""
    with patch('core.events.nats.connect') as mock_connect:
        mock_nc = AsyncMock()
        mock_connect.return_value = mock_nc
        yield mock_nc

def test_nats_connection_on_startup():
    """Test NATS connection during application startup"""
    # Test that the NATS client is properly configured in the app
    from core.events import nats_client
    assert nats_client is not None

def test_publish_rfp_parsed_event(mock_nats, auth_headers):
    """Test publishing RFP parsed event to NATS"""
    with patch('api.v1.rfps.nats_client.publish') as mock_publish:
        mock_publish.return_value = AsyncMock()
        
        # Mock the orchestrator call
        with patch('api.dependencies.call_service') as mock_call_service:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "id": "rfp-test-789",
                "project_id": "test-project-123",
                "filename": "test_rfp.txt",
                "original_filename": "test_rfp.txt",
                "file_size": 1024,
                "mime_type": "text/plain",
                "status": "parsed",
                "org_id": "test-org"
            }
            mock_call_service.return_value = mock_response
            
            files = {
                "file": ("test_rfp.txt", "Test RFP content", "text/plain")
            }
            data = {"project_id": "test-project-123"}
            
            response = client.post("/v1/rfps/ingest", files=files, data=data, headers=auth_headers)
            
            # Verify NATS publish was called
            assert mock_publish.called
            call_args = mock_publish.call_args
            assert call_args[0][0] == "rfp.parsed"  # Topic
            event_data = call_args[0][1]
            assert "rfp_id" in event_data
            assert "project_id" in event_data

def test_nats_event_structure():
    """Test NATS event structure and schema validation"""
    from aec_shared.events import RfpParsedEvent
    from aec_shared.models import Rfp, RfpStatus
    from uuid import uuid4
    from datetime import datetime
    
    # Create a proper Rfp object
    rfp = Rfp(
        id=uuid4(),
        project_id=uuid4(),
        filename="specifications.pdf",
        original_filename="specifications.pdf",
        file_size=1024,
        mime_type="application/pdf",
        status=RfpStatus.PARSED,
        parsed_data={
            "items": [
                {
                    "code": "DIV01",
                    "description": "Excavation",
                    "quantity": 100.0,
                    "unit": "cy"
                }
            ]
        },
        org_id="test-org"
    )
    
    # Test valid event creation
    event = RfpParsedEvent(
        rfp=rfp,
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
    
    assert event_dict["rfp"]["id"] == str(rfp.id)
    assert event_dict["rfp"]["project_id"] == str(rfp.project_id)
    assert event_dict["rfp"]["filename"] == "specifications.pdf"
    assert len(event_dict["parsed_items"]) == 1

def test_nats_connection_failure_graceful():
    """Test graceful handling of NATS connection failure"""
    with patch('core.events.nats.connect', side_effect=Exception("Connection failed")):
        # Application should start even if NATS fails
        test_client = TestClient(app, headers={'host': 'localhost'})
        response = test_client.get("/v1/health")
        assert response.status_code == 200

def test_nats_publish_failure_graceful(mock_nats, auth_headers):
    """Test graceful handling of NATS publish failure"""
    with patch('api.v1.rfps.nats_client.publish', side_effect=Exception("Publish failed")):
        # Mock orchestrator call to succeed
        with patch('api.dependencies.call_service') as mock_call_service:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "id": "rfp-test-789",
                "project_id": "test-project-123",
                "filename": "test_rfp.txt",
                "original_filename": "test_rfp.txt",
                "file_size": 1024,
                "mime_type": "text/plain",
                "status": "parsed",
                "org_id": "test-org"
            }
            mock_call_service.return_value = mock_response
            
            files = {
                "file": ("test_rfp.txt", "Test RFP content", "text/plain")
            }
            data = {"project_id": "test-project-123"}
            
            # RFP ingestion should still succeed even if NATS publish fails
            response = client.post("/v1/rfps/ingest", files=files, data=data, headers=auth_headers)
            assert response.status_code == 202


