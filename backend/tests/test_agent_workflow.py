





import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app (adjust path as needed)
from backend.src.backend.main import app  # Adjust this import based on your project structure

@pytest.fixture(scope="module")
def test_client():
    """Create a FastAPI test client."""
    with TestClient(app) as c:
        yield c

def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Add more tests for agent workflows, API endpoints, etc.

