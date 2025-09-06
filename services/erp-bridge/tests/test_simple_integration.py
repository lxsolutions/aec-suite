






"""
Simple integration tests for Acumatica adapter
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.adapters.acumatica.acumatica_adapter import AcumaticaAdapter
from src.adapters.base.erp_adapter import ERPConfig, Customer, Project

@pytest.fixture
def acumatica_config():
    """ERP configuration for testing"""
    return ERPConfig(
        base_url="http://localhost:8081",  # This won't exist, we'll mock it
        username="testuser",
        password="testpass",
        company="TestCompany"
    )

@pytest.fixture
def acumatica_adapter(acumatica_config):
    """Acumatica adapter instance"""
    return AcumaticaAdapter(acumatica_config)

@pytest.mark.asyncio
async def test_adapter_initialization(acumatica_adapter):
    """Test that adapter initializes correctly"""
    assert acumatica_adapter is not None
    assert acumatica_adapter.config is not None
    assert acumatica_adapter.authenticated is False
    assert acumatica_adapter.auth_cookie is None

@pytest.mark.asyncio
async def test_configuration_validation(acumatica_adapter):
    """Test that configuration is properly validated"""
    config = acumatica_adapter.config
    assert config.base_url == "http://localhost:8081"
    assert config.username == "testuser"
    assert config.password == "testpass"
    assert config.company == "TestCompany"
    assert config.timeout == 30  # Default value
    assert config.max_retries == 3  # Default value
    assert config.retry_backoff == 1.0  # Default value

@pytest.mark.asyncio
async def test_domain_object_creation():
    """Test that domain objects can be created properly"""
    customer = Customer(
        id="TEST001",
        name="Test Customer",
        email="test@example.com",
        phone="555-1234"
    )
    
    assert customer.id == "TEST001"
    assert customer.name == "Test Customer"
    assert customer.email == "test@example.com"
    assert customer.phone == "555-1234"
    
    project = Project(
        id="PROJ001",
        name="Test Project",
        customer_id="TEST001",
        status="Active"
    )
    
    assert project.id == "PROJ001"
    assert project.name == "Test Project"
    assert project.customer_id == "TEST001"
    assert project.status == "Active"

@pytest.mark.asyncio
async def test_mock_authentication(acumatica_adapter):
    """Test authentication with mocked successful response"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        # Mock successful authentication response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.cookies = {"ASP.NET_SessionId": AsyncMock(value="test-session-id")}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await acumatica_adapter.authenticate()
        
        assert result is True
        assert acumatica_adapter.authenticated is True
        assert acumatica_adapter.auth_cookie == "ASP.NET_SessionId=test-session-id"

@pytest.mark.asyncio
async def test_mock_authentication_failure(acumatica_adapter):
    """Test authentication with mocked failure response"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        # Mock failed authentication response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await acumatica_adapter.authenticate()
        
        assert result is False
        assert acumatica_adapter.authenticated is False
        assert acumatica_adapter.auth_cookie is None

@pytest.mark.asyncio
async def test_golden_path_with_mocks(acumatica_adapter):
    """Test the complete golden path using mocks"""
    # Mock authentication
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.cookies = {"ASP.NET_SessionId": AsyncMock(value="test-session-id")}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        await acumatica_adapter.authenticate()
    
    # Mock the golden path calls
    estimate_data = {
        "id": "EST001",
        "project_id": "PROJ001",
        "items": [{"description": "Test", "amount": 1000}]
    }
    
    with patch.object(acumatica_adapter, 'sync_estimate_to_budget', AsyncMock(return_value="BUDGET001")), \
         patch.object(acumatica_adapter, 'sync_budget_to_po', AsyncMock(return_value="PO001")), \
         patch.object(acumatica_adapter, 'sync_po_to_invoice', AsyncMock(return_value="INV001")):
        
        # Test the full golden path
        budget_id = await acumatica_adapter.sync_estimate_to_budget(estimate_data)
        assert budget_id == "BUDGET001"
        
        po_id = await acumatica_adapter.sync_budget_to_po(budget_id)
        assert po_id == "PO001"
        
        invoice_id = await acumatica_adapter.sync_po_to_invoice(po_id)
        assert invoice_id == "INV001"





