import pytest
from fastapi.testclient import TestClient
from services.gateway.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_project():
    """Test project creation"""
    response = client.post("/v1/projects", json={"name": "Test Project"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == "Test Project"

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
