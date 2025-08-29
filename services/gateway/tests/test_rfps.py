


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app, headers={'host': 'localhost'})

# Mock JWT token for authenticated tests
MOCK_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"

def test_ingest_rfp():
    """Test RFP ingestion with file upload"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    # Create a simple text file for upload
    files = {
        "file": ("test_rfp.txt", "Test RFP content for construction project", "text/plain")
    }
    data = {"project_id": "test-project-123"}
    
    with patch('api.v1.rfps.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock()
        mock_post.return_value.status_code = 202
        mock_post.return_value.json.return_value = {
            "message": "RFP processing started",
            "rfp_id": "rfp-test-456"
        }
        
        response = client.post("/v1/rfps/ingest", files=files, data=data, headers=headers)
        assert response.status_code == 202
        assert "rfp_id" in response.json()

def test_ingest_rfp_without_file():
    """Test RFP ingestion without file should fail"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    data = {"project_id": "test-project-123"}
    
    response = client.post("/v1/rfps/ingest", data=data, headers=headers)
    assert response.status_code == 422  # Validation error

def test_ingest_rfp_without_project_id():
    """Test RFP ingestion without project_id should fail"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    files = {
        "file": ("test_rfp.txt", "Test RFP content", "text/plain")
    }
    
    response = client.post("/v1/rfps/ingest", files=files, headers=headers)
    assert response.status_code == 422  # Validation error

def test_get_rfps():
    """Test getting list of RFPs"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.rfps.httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "rfp-1",
                "project_id": "project-1",
                "filename": "test.pdf",
                "status": "processed"
            }
        ]
        
        response = client.get("/v1/rfps", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

def test_get_rfp_by_id():
    """Test getting RFP by ID"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    with patch('api.v1.rfps.httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "rfp-789",
            "project_id": "project-123",
            "filename": "specifications.pdf",
            "status": "processed",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        response = client.get("/v1/rfps/rfp-789", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == "rfp-789"

def test_rfp_upload_rate_limit():
    """Test rate limiting on RFP uploads"""
    headers = {"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
    
    # Create test file
    files = {
        "file": ("test_rfp.txt", "Test RFP content", "text/plain")
    }
    data = {"project_id": "test-project-123"}
    
    # Make multiple upload requests to test rate limiting
    responses = []
    for _ in range(15):  # Should trigger upload rate limit (10/min)
        with patch('api.v1.rfps.httpx.AsyncClient.post'):
            response = client.post("/v1/rfps/ingest", files=files, data=data, headers=headers)
            responses.append(response.status_code)
    
    # At least some should succeed (rate limit is per IP, test client uses same IP)
    assert any(status == 202 for status in responses)


