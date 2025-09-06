





"""
Mock ERP server for testing Acumatica/Odoo adapters
"""

from aiohttp import web
import json
import asyncio
from datetime import datetime

class MockERPServer:
    """Mock ERP server that simulates Acumatica/Odoo API responses"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.session_cookie = "ASP.NET_SessionId=mock-session-id"
        self.authenticated = False
    
    def setup_routes(self):
        """Setup mock API routes"""
        self.app.router.add_post('/entity/auth/login', self.handle_login)
        self.app.router.add_post('/entity/Default/20.200.001/Customer', self.handle_create_customer)
        self.app.router.add_post('/entity/Default/20.200.001/Project', self.handle_create_project)
        self.app.router.add_post('/entity/Default/20.200.001/InventoryItem', self.handle_create_item)
        self.app.router.add_post('/entity/Default/20.200.001/PurchaseOrder', self.handle_create_po)
        self.app.router.add_post('/entity/Default/20.200.001/Invoice', self.handle_create_invoice)
        self.app.router.add_post('/entity/Default/20.200.001/ProjectBudget', self.handle_create_budget)
        self.app.router.add_post('/entity/Default/20.200.001/APBill', self.handle_create_ap_bill)
        
        # GET endpoints
        self.app.router.add_get('/entity/Default/20.200.001/Customer/{id}', self.handle_get_customer)
        self.app.router.add_get('/entity/Default/20.200.001/Project/{id}', self.handle_get_project)
        self.app.router.add_get('/entity/Default/20.200.001/InventoryItem/{id}', self.handle_get_item)
        self.app.router.add_get('/entity/Default/20.200.001/PurchaseOrder/{id}', self.handle_get_po)
        self.app.router.add_get('/entity/Default/20.200.001/ProjectBudget/{id}', self.handle_get_budget)
    
    async def handle_login(self, request):
        """Handle authentication"""
        data = await request.json()
        if data.get('name') and data.get('password'):
            self.authenticated = True
            return web.Response(
                status=200,
                headers={'Set-Cookie': self.session_cookie},
                text=json.dumps({"status": "success"})
            )
        return web.Response(status=401, text=json.dumps({"error": "Invalid credentials"}))
    
    async def handle_create_customer(self, request):
        """Handle customer creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        customer_id = data.get('CustomerID', {}).get('value', 'CUST' + str(int(datetime.now().timestamp())))
        
        response = {
            "CustomerID": {"value": customer_id},
            "CustomerName": data.get('CustomerName', {}).get('value', ''),
            "Status": {"value": "Active"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_project(self, request):
        """Handle project creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        project_id = data.get('ProjectID', {}).get('value', 'PROJ' + str(int(datetime.now().timestamp())))
        
        response = {
            "ProjectID": {"value": project_id},
            "Description": data.get('Description', {}).get('value', ''),
            "Status": {"value": "Active"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_item(self, request):
        """Handle item creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        item_id = data.get('InventoryID', {}).get('value', 'ITEM' + str(int(datetime.now().timestamp())))
        
        response = {
            "InventoryID": {"value": item_id},
            "Description": data.get('Description', {}).get('value', ''),
            "BasePrice": data.get('BasePrice', {}).get('value', 0)
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_po(self, request):
        """Handle purchase order creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        po_id = 'PO' + str(int(datetime.now().timestamp()))
        
        response = {
            "OrderNbr": {"value": po_id},
            "VendorID": data.get('VendorID', {}).get('value', ''),
            "Description": data.get('Description', {}).get('value', '')
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_invoice(self, request):
        """Handle invoice creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        invoice_id = 'INV' + str(int(datetime.now().timestamp()))
        
        response = {
            "ReferenceNbr": {"value": invoice_id},
            "CustomerID": data.get('CustomerID', {}).get('value', ''),
            "Description": data.get('Description', {}).get('value', '')
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_budget(self, request):
        """Handle budget creation"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        budget_id = 'BUDGET' + str(int(datetime.now().timestamp()))
        
        response = {
            "BudgetID": {"value": budget_id},
            "ProjectID": data.get('ProjectID', {}).get('value', ''),
            "Description": data.get('Description', {}).get('value', '')
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_create_ap_bill(self, request):
        """Handle AP bill creation (invoice)"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        data = await request.json()
        bill_id = 'BILL' + str(int(datetime.now().timestamp()))
        
        response = {
            "ReferenceNbr": {"value": bill_id},
            "VendorID": data.get('VendorID', {}).get('value', ''),
            "Description": data.get('Description', {}).get('value', '')
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_get_customer(self, request):
        """Handle customer retrieval"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        customer_id = request.match_info['id']
        response = {
            "CustomerID": {"value": customer_id},
            "CustomerName": {"value": f"Customer {customer_id}"},
            "Status": {"value": "Active"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_get_project(self, request):
        """Handle project retrieval"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        project_id = request.match_info['id']
        response = {
            "ProjectID": {"value": project_id},
            "Description": {"value": f"Project {project_id}"},
            "Status": {"value": "Active"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_get_item(self, request):
        """Handle item retrieval"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        item_id = request.match_info['id']
        response = {
            "InventoryID": {"value": item_id},
            "Description": {"value": f"Item {item_id}"},
            "BasePrice": {"value": 100.0}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_get_po(self, request):
        """Handle PO retrieval"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        po_id = request.match_info['id']
        response = {
            "OrderNbr": {"value": po_id},
            "VendorID": {"value": "VENDOR001"},
            "Description": {"value": f"PO {po_id}"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    async def handle_get_budget(self, request):
        """Handle budget retrieval"""
        if not self._check_auth(request):
            return web.Response(status=401)
        
        budget_id = request.match_info['id']
        response = {
            "BudgetID": {"value": budget_id},
            "ProjectID": {"value": "PROJ001"},
            "Description": {"value": f"Budget {budget_id}"}
        }
        return web.Response(status=200, text=json.dumps(response))
    
    def _check_auth(self, request):
        """Check if request is authenticated"""
        cookie_header = request.headers.get('Cookie', '')
        return self.authenticated and self.session_cookie in cookie_header
    
    async def start(self):
        """Start the mock server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, self.host, self.port)
        await self.site.start()
        print(f"Mock ERP server started at http://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the mock server"""
        await self.site.stop()
        print("Mock ERP server stopped")

async def main():
    """Main function to run the mock server"""
    server = MockERPServer()
    await server.start()
    
    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())




