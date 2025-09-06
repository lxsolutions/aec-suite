




"""
Acumatica ERP adapter implementation
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from urllib.parse import urljoin
import json

from ..base.erp_adapter import ERPAdapter, ERPConfig, Customer, Project, Item, PurchaseOrder, Invoice

logger = logging.getLogger(__name__)

class AcumaticaAdapter(ERPAdapter):
    """Acumatica ERP system adapter"""
    
    def __init__(self, config: ERPConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_cookie: Optional[str] = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Acumatica using basic auth"""
        try:
            auth_url = urljoin(self.config.base_url, "entity/auth/login")
            auth_data = {
                "name": self.config.username,
                "password": self.config.password,
                "company": self.config.company
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    auth_url,
                    json=auth_data,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        # Acumatica returns auth cookie in response
                        cookies = response.cookies
                        if "ASP.NET_SessionId" in cookies:
                            self.auth_cookie = f"ASP.NET_SessionId={cookies['ASP.NET_SessionId'].value}"
                            self.authenticated = True
                            logger.info("Successfully authenticated with Acumatica")
                            return True
            
            logger.error("Acumatica authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"Acumatica authentication error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Acumatica API"""
        self._ensure_authenticated()
        
        url = urljoin(self.config.base_url, endpoint)
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.auth_cookie
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, url, headers=headers, timeout=self.config.timeout, **kwargs
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 401:
                            # Re-authenticate and retry
                            await self.authenticate()
                            continue
                        else:
                            logger.error(f"Acumatica API error: {response.status} - {await response.text()}")
                            return None
                            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Acumatica request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_backoff * (2 ** attempt))
                else:
                    logger.error(f"All Acumatica request attempts failed: {e}")
                    return None
        
        return None
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID from Acumatica"""
        endpoint = f"entity/Default/20.200.001/Customer/{customer_id}"
        response = await self._make_request("GET", endpoint)
        
        if response:
            return Customer(
                id=response.get("CustomerID", {}).get("value", ""),
                name=response.get("CustomerName", {}).get("value", ""),
                email=response.get("MainContact", {}).get("Email", {}).get("value"),
                phone=response.get("MainContact", {}).get("Phone", {}).get("value"),
                external_id=response.get("CustomerID", {}).get("value")
            )
        return None
    
    async def create_customer(self, customer: Customer) -> Optional[Customer]:
        """Create a new customer in Acumatica"""
        endpoint = "entity/Default/20.200.001/Customer"
        customer_data = {
            "CustomerID": {"value": customer.id},
            "CustomerName": {"value": customer.name},
            "MainContact": {
                "Email": {"value": customer.email},
                "Phone": {"value": customer.phone}
            },
            "Status": {"value": "Active"}
        }
        
        response = await self._make_request("POST", endpoint, json=customer_data)
        if response:
            return customer
        return None
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID from Acumatica"""
        endpoint = f"entity/Default/20.200.001/Project/{project_id}"
        response = await self._make_request("GET", endpoint)
        
        if response:
            return Project(
                id=response.get("ProjectID", {}).get("value", ""),
                name=response.get("Description", {}).get("value", ""),
                customer_id=response.get("Customer", {}).get("value", ""),
                status=response.get("Status", {}).get("value", "Active"),
                external_id=response.get("ProjectID", {}).get("value")
            )
        return None
    
    async def create_project(self, project: Project) -> Optional[Project]:
        """Create a new project in Acumatica"""
        endpoint = "entity/Default/20.200.001/Project"
        project_data = {
            "ProjectID": {"value": project.id},
            "Description": {"value": project.name},
            "Customer": {"value": project.customer_id},
            "Status": {"value": "Active"}
        }
        
        response = await self._make_request("POST", endpoint, json=project_data)
        if response:
            return project
        return None
    
    async def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID from Acumatica"""
        endpoint = f"entity/Default/20.200.001/InventoryItem/{item_id}"
        response = await self._make_request("GET", endpoint)
        
        if response:
            return Item(
                id=response.get("InventoryID", {}).get("value", ""),
                name=response.get("Description", {}).get("value", ""),
                description=response.get("ItemClass", {}).get("value"),
                unit_price=float(response.get("BasePrice", {}).get("value", 0)),
                unit_of_measure=response.get("UOM", {}).get("value"),
                external_id=response.get("InventoryID", {}).get("value")
            )
        return None
    
    async def create_item(self, item: Item) -> Optional[Item]:
        """Create a new item in Acumatica"""
        endpoint = "entity/Default/20.200.001/InventoryItem"
        item_data = {
            "InventoryID": {"value": item.id},
            "Description": {"value": item.name},
            "ItemClass": {"value": item.category or "STANDARD"},
            "BasePrice": {"value": item.unit_price or 0},
            "UOM": {"value": item.unit_of_measure or "EA"}
        }
        
        response = await self._make_request("POST", endpoint, json=item_data)
        if response:
            return item
        return None
    
    async def create_purchase_order(self, po: PurchaseOrder) -> Optional[PurchaseOrder]:
        """Create a purchase order in Acumatica"""
        endpoint = "entity/Default/20.200.001/PurchaseOrder"
        po_data = {
            "OrderType": {"value": "Normal"},
            "VendorID": {"value": po.vendor_id},
            "Description": {"value": f"PO for Project {po.project_id}"},
            "Details": [
                {
                    "InventoryID": {"value": item["item_id"]},
                    "Quantity": {"value": item["quantity"]},
                    "UnitCost": {"value": item["unit_price"]},
                    "ExtendedCost": {"value": item["quantity"] * item["unit_price"]}
                } for item in po.items
            ]
        }
        
        response = await self._make_request("POST", endpoint, json=po_data)
        if response:
            po.external_id = response.get("OrderNbr", {}).get("value")
            return po
        return None
    
    async def create_invoice(self, invoice: Invoice) -> Optional[Invoice]:
        """Create an invoice in Acumatica"""
        endpoint = "entity/Default/20.200.001/Invoice"
        invoice_data = {
            "Type": {"value": "Invoice"},
            "CustomerID": {"value": invoice.customer_id},
            "Description": {"value": f"Invoice for Project {invoice.project_id}"},
            "Details": [
                {
                    "InventoryID": {"value": item["item_id"]},
                    "Quantity": {"value": item["quantity"]},
                    "UnitPrice": {"value": item["unit_price"]},
                    "ExtendedPrice": {"value": item["quantity"] * item["unit_price"]}
                } for item in invoice.items
            ]
        }
        
        response = await self._make_request("POST", endpoint, json=invoice_data)
        if response:
            invoice.external_id = response.get("ReferenceNbr", {}).get("value")
            return invoice
        return None
    
    async def sync_estimate_to_budget(self, estimate_data: Dict[str, Any]) -> Optional[str]:
        """Sync estimate to budget in Acumatica"""
        # Extract estimate information
        estimate_id = estimate_data.get("id", "")
        project_id = estimate_data.get("project_id", "")
        items = estimate_data.get("items", [])
        
        # Create budget in Acumatica (simplified)
        budget_data = {
            "ProjectID": {"value": project_id},
            "Description": {"value": f"Budget from Estimate {estimate_id}"},
            "Status": {"value": "Active"},
            "Details": [
                {
                    "AccountID": {"value": "40100"},  # Revenue account
                    "Description": {"value": item.get("description", "")},
                    "Amount": {"value": item.get("amount", 0)}
                } for item in items
            ]
        }
        
        endpoint = "entity/Default/20.200.001/ProjectBudget"
        response = await self._make_request("POST", endpoint, json=budget_data)
        
        if response:
            budget_id = response.get("BudgetID", {}).get("value")
            logger.info(f"Estimate {estimate_id} synced to budget {budget_id}")
            return budget_id
        
        return None
    
    async def sync_budget_to_po(self, budget_id: str) -> Optional[str]:
        """Sync budget to purchase order in Acumatica"""
        # This would typically involve more complex logic to convert budget items to POs
        # For now, we'll create a simple PO based on the budget
        
        endpoint = f"entity/Default/20.200.001/ProjectBudget/{budget_id}"
        budget_data = await self._make_request("GET", endpoint)
        
        if not budget_data:
            return None
        
        # Create PO from budget (simplified)
        po_data = {
            "OrderType": {"value": "Normal"},
            "VendorID": {"value": "DEFAULT_VENDOR"},
            "Description": {"value": f"PO from Budget {budget_id}"},
            "Details": [
                {
                    "InventoryID": {"value": "SERVICE001"},
                    "Quantity": {"value": 1},
                    "UnitCost": {"value": 1000},  # Simplified amount
                    "Description": {"value": "Budget implementation services"}
                }
            ]
        }
        
        po_endpoint = "entity/Default/20.200.001/PurchaseOrder"
        response = await self._make_request("POST", po_endpoint, json=po_data)
        
        if response:
            po_id = response.get("OrderNbr", {}).get("value")
            logger.info(f"Budget {budget_id} synced to PO {po_id}")
            return po_id
        
        return None
    
    async def sync_po_to_invoice(self, po_id: str) -> Optional[str]:
        """Sync purchase order to invoice in Acumatica"""
        # Get PO details
        endpoint = f"entity/Default/20.200.001/PurchaseOrder/{po_id}"
        po_data = await self._make_request("GET", endpoint)
        
        if not po_data:
            return None
        
        # Create invoice from PO (simplified)
        vendor_id = po_data.get("VendorID", {}).get("value", "UNKNOWN")
        
        invoice_data = {
            "Type": {"value": "Invoice"},
            "VendorID": {"value": vendor_id},
            "Description": {"value": f"Invoice from PO {po_id}"},
            "Details": [
                {
                    "InventoryID": {"value": detail.get("InventoryID", {}).get("value", "")},
                    "Quantity": {"value": detail.get("Quantity", {}).get("value", 1)},
                    "UnitPrice": {"value": detail.get("UnitCost", {}).get("value", 0)},
                    "Description": {"value": detail.get("Description", {}).get("value", "")}
                } for detail in po_data.get("Details", [])
            ]
        }
        
        invoice_endpoint = "entity/Default/20.200.001/APBill"
        response = await self._make_request("POST", invoice_endpoint, json=invoice_data)
        
        if response:
            invoice_id = response.get("ReferenceNbr", {}).get("value")
            logger.info(f"PO {po_id} synced to invoice {invoice_id}")
            return invoice_id
        
        return None



