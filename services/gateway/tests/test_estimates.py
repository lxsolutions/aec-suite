import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, headers={'host': 'localhost'})

def test_health_check():
    """Test health endpoint"""
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "gateway"}

def test_create_project(test_client, auth_headers):
    """Test project creation"""
    project_data = {
        "name": "Test Project",
        "client_id": "test-client-123",
        "start_date": "2024-01-01"
    }
    response = test_client.post("/v1/projects", json=project_data, headers=auth_headers)
    assert response.status_code == 201  # Created status
    assert "id" in response.json()
    assert response.json()["name"] == "Test Project"  # Mock response from orchestrator

def test_create_estimate():
    """Test estimate creation"""
    payload = {
        "project_id": "test-project-123",
        "items": [
            {
                "code": "DIV01",
                "description": "Excavation",
                "uom": "cy",
                "qty": 100.0,
                "unit_cost": 25.0
            }
        ],
        "currency": "USD"
    }
    response = client.post("/v1/estimates", json=payload)
    assert response.status_code == 200
    assert response.json()["project_id"] == "test-project-123"
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["code"] == "DIV01"

def test_ingest_rfp():
    """Test RFP ingestion"""
    # Create a simple text file for upload
    files = {"file": ("test_rfp.txt", "Test RFP content", "text/plain")}
    response = client.post("/v1/estimates/rfp:ingest", files=files)
    assert response.status_code == 200
    assert response.json()["project_id"] == "stub-project"
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["code"] == "DIV01"
