





"""
Integration tests for Acumatica adapter with mock ERP server
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch

from src.adapters.acumatica.acumatica_adapter import AcumaticaAdapter
from src.adapters.base.erp_adapter import ERPConfig, Customer, Project, Item

@pytest.fixture
async def mock_erp_server():
    """Fixture to start/stop mock ERP server"""
    from .mock_erp_server import MockERPServer
    
    server = MockERPServer(host='localhost', port=8081)  # Use different port
    await server.start()
    
    yield server
    
    await server.stop()

@pytest.fixture
def acumatica_config():
    """ERP configuration for mock server"""
    return ERPConfig(
        base_url="http://localhost:8081",
        username="testuser",
        password="testpass",
        company="TestCompany",
        timeout=5,
        max_retries=2,
        retry_backoff=0.1
    )

@pytest.fixture
def acumatica_adapter(acumatica_config):
    """Acumatica adapter instance"""
    return AcumaticaAdapter(acumatica_config)

@pytest.mark.asyncio
async def test_adapter_authentication_integration(mock_erp_server, acumatica_adapter):
    """Test authentication with mock ERP server"""
    result = await acumatica_adapter.authenticate()
    
    assert result is True
    assert acumatica_adapter.authenticated is True
    assert acumatica_adapter.auth_cookie is not None

@pytest.mark.asyncio
async def test_create_customer_integration(mock_erp_server, acumatica_adapter):
    """Test customer creation with mock ERP server"""
    # First authenticate
    await acumatica_adapter.authenticate()
    
    customer = Customer(
        id="TESTCUST001",
        name="Integration Test Customer",
        email="test@example.com",
        phone="555-1234"
    )
    
    result = await acumatica_adapter.create_customer(customer)
    
    assert result is not None
    assert result.id == customer.id
    assert result.name == customer.name

@pytest.mark.asyncio
async def test_create_project_integration(mock_erp_server, acumatica_adapter):
    """Test project creation with mock ERP server"""
    await acumatica_adapter.authenticate()
    
    project = Project(
        id="TESTPROJ001",
        name="Integration Test Project",
        customer_id="TESTCUST001",
        status="Active"
    )
    
    result = await acumatica_adapter.create_project(project)
    
    assert result is not None
    assert result.id == project.id
    assert result.name == project.name

@pytest.mark.asyncio
async def test_golden_path_integration(mock_erp_server, acumatica_adapter):
    """Test golden path sync with mock ERP server"""
    await acumatica_adapter.authenticate()
    
    estimate_data = {
        "id": "TESTEST001",
        "project_id": "TESTPROJ001",
        "items": [
            {"description": "Test Item 1", "amount": 1000},
            {"description": "Test Item 2", "amount": 2000}
        ]
    }
    
    # Test estimate → budget sync
    budget_id = await acumatica_adapter.sync_estimate_to_budget(estimate_data)
    assert budget_id is not None
    assert budget_id.startswith("BUDGET")
    
    # Test budget → PO sync
    po_id = await acumatica_adapter.sync_budget_to_po(budget_id)
    assert po_id is not None
    assert po_id.startswith("PO")
    
    # Test PO → invoice sync
    invoice_id = await acumatica_adapter.sync_po_to_invoice(po_id)
    assert invoice_id is not None
    assert invoice_id.startswith("BILL")

@pytest.mark.asyncio
async def test_retry_mechanism_integration(mock_erp_server, acumatica_adapter):
    """Test retry mechanism with temporary server failure"""
    await acumatica_adapter.authenticate()
    
    # Temporarily disable authentication to simulate server error
    original_auth = mock_erp_server.authenticated
    mock_erp_server.authenticated = False
    
    try:
        # This should trigger retry mechanism
        customer = Customer(
            id="RETRYTEST",
            name="Retry Test Customer"
        )
        
        # The request should fail due to authentication error
        result = await acumatica_adapter.create_customer(customer)
        assert result is None  # Should return None after retries exhausted
        
    finally:
        # Restore authentication
        mock_erp_server.authenticated = original_auth

@pytest.mark.asyncio
async def test_error_handling_integration():
    """Test error handling with invalid server URL"""
    # Create adapter with invalid URL
    config = ERPConfig(
        base_url="http://invalid-server:9999",
        username="test",
        password="test",
        company="test"
    )
    
    adapter = AcumaticaAdapter(config)
    
    # Authentication should fail
    result = await adapter.authenticate()
    assert result is False
    
    # Any subsequent operation should also fail gracefully
    customer = Customer(id="TEST", name="Test")
    result = await adapter.create_customer(customer)
    assert result is None




