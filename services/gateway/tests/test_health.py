


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app, headers={'host': 'localhost'})

def test_health_check():
    """Test health endpoint"""
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "gateway"}

def test_healthz():
    """Test healthz endpoint (k8s health check)"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_readyz():
    """Test readyz endpoint (k8s readiness check)"""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_health_check_with_dependencies():
    """Test health check with dependency status"""
    # Mock database connection check
    with patch('api.v1.health.check_database_connection') as mock_db_check:
        mock_db_check.return_value = True
        
        # Mock NATS connection check
        with patch('api.v1.health.check_nats_connection') as mock_nats_check:
            mock_nats_check.return_value = True
            
            response = client.get("/v1/health?detailed=true")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["dependencies"]["database"] == "connected"
            assert data["dependencies"]["nats"] == "connected"

def test_health_check_with_failed_dependencies():
    """Test health check with failed dependencies"""
    # Mock database connection failure
    with patch('api.v1.health.check_database_connection') as mock_db_check:
        mock_db_check.return_value = False
        
        # Mock NATS connection failure
        with patch('api.v1.health.check_nats_connection') as mock_nats_check:
            mock_nats_check.return_value = False
            
            response = client.get("/v1/health?detailed=true")
            assert response.status_code == 503  # Service Unavailable
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["dependencies"]["database"] == "disconnected"
            assert data["dependencies"]["nats"] == "disconnected"

def test_health_check_rate_limit():
    """Test rate limiting on health endpoints"""
    # Make multiple health check requests
    responses = []
    for _ in range(150):  # Should be under default rate limit (100/min)
        response = client.get("/v1/health")
        responses.append(response.status_code)
    
    # All should succeed (health checks typically have higher limits)
    assert all(status == 200 for status in responses)


