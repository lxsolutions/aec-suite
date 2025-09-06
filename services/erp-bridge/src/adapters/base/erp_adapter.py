



"""
Base ERP adapter interface for all ERP system integrations
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ERPConfig:
    """Configuration for ERP adapter"""
    base_url: str
    username: str
    password: str
    company: str
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 1.0

@dataclass
class Customer:
    """Customer/Client domain object"""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Project:
    """Project/Job domain object"""
    id: str
    name: str
    customer_id: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Item:
    """Item domain object"""
    id: str
    name: str
    description: Optional[str] = None
    unit_price: Optional[float] = None
    unit_of_measure: Optional[str] = None
    category: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PurchaseOrder:
    """Purchase Order domain object"""
    id: str
    project_id: str
    vendor_id: str
    status: str
    total_amount: float
    order_date: datetime
    items: List[Dict[str, Any]]
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Invoice:
    """Invoice domain object"""
    id: str
    project_id: str
    customer_id: str
    status: str
    total_amount: float
    invoice_date: datetime
    due_date: datetime
    items: List[Dict[str, Any]]
    external_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ERPAdapter(ABC):
    """Abstract base class for all ERP adapters"""
    
    def __init__(self, config: ERPConfig):
        self.config = config
        self.authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the ERP system"""
        pass
    
    @abstractmethod
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        pass
    
    @abstractmethod
    async def create_customer(self, customer: Customer) -> Optional[Customer]:
        """Create a new customer"""
        pass
    
    @abstractmethod
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        pass
    
    @abstractmethod
    async def create_project(self, project: Project) -> Optional[Project]:
        """Create a new project"""
        pass
    
    @abstractmethod
    async def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID"""
        pass
    
    @abstractmethod
    async def create_item(self, item: Item) -> Optional[Item]:
        """Create a new item"""
        pass
    
    @abstractmethod
    async def create_purchase_order(self, po: PurchaseOrder) -> Optional[PurchaseOrder]:
        """Create a purchase order"""
        pass
    
    @abstractmethod
    async def create_invoice(self, invoice: Invoice) -> Optional[Invoice]:
        """Create an invoice"""
        pass
    
    @abstractmethod
    async def sync_estimate_to_budget(self, estimate_data: Dict[str, Any]) -> Optional[str]:
        """Sync estimate to budget in ERP system"""
        pass
    
    @abstractmethod
    async def sync_budget_to_po(self, budget_id: str) -> Optional[str]:
        """Sync budget to purchase order in ERP system"""
        pass
    
    @abstractmethod
    async def sync_po_to_invoice(self, po_id: str) -> Optional[str]:
        """Sync purchase order to invoice in ERP system"""
        pass
    
    def _ensure_authenticated(self):
        """Ensure adapter is authenticated before making requests"""
        if not self.authenticated:
            raise RuntimeError("ERP adapter not authenticated. Call authenticate() first.")


