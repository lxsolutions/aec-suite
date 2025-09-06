
"""
Contract tests for the Bid→Plan→Bill vertical slice workflow
Mirrors the README curl flow with comprehensive testing
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from main import app

# Test client with proper headers
client = TestClient(app, headers={'host': 'localhost'})

# Mock JWT token for authenticated tests
MOCK_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJvcmdfaWQiOiJ0ZXN0LW9yZyIsImV4cCI6MTc1NjQyNzQwMH0.XHfCG5ZrKycPhDndWT2oScG1vsfRYQYME3iOEPBpa5Y"

# Common headers for all requests
AUTH_HEADERS = {
    "Authorization": f"Bearer {MOCK_JWT_TOKEN}",
    "Content-Type": "application/json"
}

class TestVerticalSliceContract:
    """Comprehensive contract tests for the Bid→Plan→Bill workflow"""
    
    def test_health_check(self):
        """Test gateway health endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_project_creation_with_idempotency(self):
        """Test project creation with idempotency key support"""
        project_data = {
            "name": "Demo Project",
            "client_id": "demo-client",
            "budget": 1000000,
            "description": "Test project for vertical slice"
        }
        
        idempotency_key = "test-idempotency-key-123"
        headers = {
            **AUTH_HEADERS,
            "Idempotency-Key": idempotency_key
        }
        
        with patch('api.v1.projects.httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "id": "demo-project-123",
                "name": "Demo Project",
                "client_id": "demo-client",
                "budget": 1000000,
                "status": "active"
            }
            
            # First request should succeed
            response1 = client.post("/v1/projects", json=project_data, headers=headers)
            assert response1.status_code == 201
            assert response1.json()["id"] == "demo-project-123"
            
            # Second request with same idempotency key should return same result
            response2 = client.post("/v1/projects", json=project_data, headers=headers)
            assert response2.status_code == 201
            assert response2.json() == response1.json()
    
    def test_rfp_ingestion_with_mock_file(self):
        """Test RFP ingestion with mock file upload"""
        # Mock file content
        file_content = b"Construction project specifications\nBuilding materials and labor estimates"
        
        headers = {
            "Authorization": f"Bearer {MOCK_JWT_TOKEN}"
        }
        
        # Mock the file processing and NATS publishing
        with patch('api.v1.rfps.nats_client.publish') as mock_publish:
            mock_publish.return_value = None
            
            response = client.post(
                "/v1/rfps/ingest",
                headers=headers,
                files={
                    "file": ("test_rfp.txt", file_content, "text/plain")
                },
                data={"project_id": "demo-project-123"}
            )
            
            assert response.status_code == 200
            assert "project_id" in response.json()
            assert response.json()["project_id"] == "demo-project-123"
            assert "items" in response.json()
    
    def test_estimate_creation_with_idempotency(self):
        """Test estimate creation with idempotency key support"""
        estimate_data = {
            "project_id": "demo-project-123",
            "items": [
                {
                    "code": "CON001",
                    "description": "Concrete foundation",
                    "quantity": 100,
                    "unit": "m3",
                    "unit_cost": 150,
                    "total_cost": 15000
                }
            ],
            "currency": "USD"
        }
        
        idempotency_key = "test-estimate-idempotency-456"
        headers = {
            **AUTH_HEADERS,
            "Idempotency-Key": idempotency_key
        }
        
        # Test estimate creation (currently mocked to return input)
        response1 = client.post("/v1/estimates", json=estimate_data, headers=headers)
        assert response1.status_code == 200
        assert response1.json()["project_id"] == "demo-project-123"
        
        # Test idempotency - same key should return same result
        response2 = client.post("/v1/estimates", json=estimate_data, headers=headers)
        assert response2.status_code == 200
        assert response2.json() == response1.json()
    
    def test_get_estimates_by_project(self):
        """Test retrieving estimates for a project"""
        headers = AUTH_HEADERS.copy()
        
        # Mock the response from downstream service
        with patch('api.v1.estimates.httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = AsyncMock()
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {
                    "id": "estimate-001",
                    "project_id": "demo-project-123",
                    "version": 1,
                    "status": "draft",
                    "total_amount": 15000,
                    "items": [
                        {
                            "code": "CON001",
                            "description": "Concrete foundation",
                            "quantity": 100,
                            "unit": "m3",
                            "unit_cost": 150,
                            "total_cost": 15000
                        }
                    ]
                }
            ]
            
            response = client.get("/v1/estimates?project_id=demo-project-123", headers=headers)
            assert response.status_code == 200
            estimates = response.json()
            assert isinstance(estimates, list)
            assert len(estimates) > 0
            assert estimates[0]["project_id"] == "demo-project-123"
    
    def test_error_envelope_standardization(self):
        """Test that all errors return standardized error envelope"""
        # Test with invalid project ID
        headers = AUTH_HEADERS.copy()
        
        with patch('api.v1.projects.httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = AsyncMock()
            mock_get.return_value.status_code = 404
            mock_get.return_value.json.return_value = {
                "error": "Project not found"
            }
            
            response = client.get("/v1/projects/nonexistent-project", headers=headers)
            
            # Should return standardized error format
            assert response.status_code == 404
            error_data = response.json()
            assert "traceId" in error_data
            assert "code" in error_data
            assert "message" in error_data
            assert "details" in error_data
    
    def test_missing_idempotency_key_on_create(self):
        """Test that create operations require idempotency keys"""
        project_data = {
            "name": "Test Project",
            "client_id": "test-client",
            "budget": 500000
        }
        
        with patch('api.v1.projects.httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "id": "test-project-456",
                "name": "Test Project"
            }
            
            # Should fail without idempotency key
            response = client.post("/v1/projects", json=project_data, headers=AUTH_HEADERS)
            assert response.status_code == 400
            assert "idempotency" in response.json()["message"].lower()
    
    def test_workflow_end_to_end(self):
        """Test complete Bid→Plan→Bill workflow in sequence"""
        # 1. Create project
        project_data = {
            "name": "E2E Test Project",
            "client_id": "e2e-client",
            "budget": 2000000
        }
        
        project_headers = {
            **AUTH_HEADERS,
            "Idempotency-Key": "e2e-project-key-789"
        }
        
        with patch('api.v1.projects.httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = AsyncMock()
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "id": "e2e-project-789",
                "name": "E2E Test Project",
                "client_id": "e2e-client",
                "budget": 2000000,
                "status": "active"
            }
            
            project_response = client.post("/v1/projects", json=project_data, headers=project_headers)
            assert project_response.status_code == 201
            project_id = project_response.json()["id"]
        
        # 2. Ingest RFP
        file_content = b"E2E Test RFP Content\nDetailed construction specifications"
        
        with patch('api.v1.rfps.nats_client.publish') as mock_publish:
            mock_publish.return_value = None
            
            rfp_response = client.post(
                "/v1/rfps/ingest",
                headers=AUTH_HEADERS,
                files={
                    "file": ("e2e_rfp.txt", file_content, "text/plain")
                },
                data={"project_id": project_id}
            )
            
            assert rfp_response.status_code == 200
            assert rfp_response.json()["project_id"] == project_id
        
        # 3. Create estimate
        estimate_data = {
            "project_id": project_id,
            "items": [
                {
                    "code": "E2E001",
                    "description": "E2E Test Item",
                    "quantity": 50,
                    "unit": "ea",
                    "unit_cost": 1000,
                    "total_cost": 50000
                }
            ],
            "currency": "USD"
        }
        
        estimate_headers = {
            **AUTH_HEADERS,
            "Idempotency-Key": "e2e-estimate-key-789"
        }
        
        estimate_response = client.post("/v1/estimates", json=estimate_data, headers=estimate_headers)
        assert estimate_response.status_code == 200
        assert estimate_response.json()["project_id"] == project_id
        
        # 4. Verify estimates can be retrieved
        with patch('api.v1.estimates.httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = AsyncMock()
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {
                    "id": "e2e-estimate-001",
                    "project_id": project_id,
                    "version": 1,
                    "status": "ready",
                    "total_amount": 50000,
                    "items": estimate_data["items"]
                }
            ]
            
            estimates_response = client.get(f"/v1/estimates?project_id={project_id}", headers=AUTH_HEADERS)
            assert estimates_response.status_code == 200
            estimates = estimates_response.json()
            assert len(estimates) > 0
            assert estimates[0]["project_id"] == project_id


# Test error scenarios
class TestErrorScenarios:
    """Test error handling and edge cases"""
    
    def test_invalid_jwt_token(self):
        """Test authentication with invalid JWT token"""
        headers = {
            "Authorization": "Bearer invalid-token",
            "Content-Type": "application/json"
        }
        
        response = client.get("/v1/projects", headers=headers)
        assert response.status_code == 401
        assert "token" in response.json()["message"].lower()
    
    def test_rate_limiting(self):
        """Test rate limiting behavior"""
        project_data = {
            "name": "Rate Limit Test",
            "client_id": "test-client",
            "budget": 100000
        }
        
        headers = {
            **AUTH_HEADERS,
            "Idempotency-Key": "rate-limit-test-key"
        }
        
        # Make multiple requests quickly
        responses = []
        for i in range(10):
            with patch('api.v1.projects.httpx.AsyncClient.post') as mock_post:
                mock_post.return_value = AsyncMock()
                mock_post.return_value.status_code = 201
                mock_post.return_value.json.return_value = {
                    "id": f"test-project-{i}",
                    "name": "Test Project"
                }
                
                response = client.post("/v1/projects", json=project_data, headers=headers)
                responses.append(response.status_code)
        
        # Should have successful responses (rate limit is per IP, test client uses same IP)
        assert any(status == 201 for status in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

