




"""
Configuration and factory for ERP adapters
"""

import os
from typing import Optional
from dataclasses import dataclass

from .base.erp_adapter import ERPConfig, ERPAdapter
from .acumatica.acumatica_adapter import AcumaticaAdapter

@dataclass
class ERPAdapterConfig:
    """ERP adapter configuration from environment"""
    adapter_type: str
    base_url: str
    username: str
    password: str
    company: str
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 1.0

def get_erp_adapter_config() -> Optional[ERPAdapterConfig]:
    """Get ERP adapter configuration from environment variables"""
    adapter_type = os.getenv("ERP_ADAPTER_TYPE", "acumatica").lower()
    base_url = os.getenv("ERP_BASE_URL")
    username = os.getenv("ERP_USERNAME")
    password = os.getenv("ERP_PASSWORD")
    company = os.getenv("ERP_COMPANY", "Default")
    
    if not all([base_url, username, password]):
        return None
    
    return ERPAdapterConfig(
        adapter_type=adapter_type,
        base_url=base_url,
        username=username,
        password=password,
        company=company,
        timeout=int(os.getenv("ERP_TIMEOUT", "30")),
        max_retries=int(os.getenv("ERP_MAX_RETRIES", "3")),
        retry_backoff=float(os.getenv("ERP_RETRY_BACKOFF", "1.0"))
    )

def create_erp_adapter(config: ERPAdapterConfig) -> Optional[ERPAdapter]:
    """Create appropriate ERP adapter based on configuration"""
    erp_config = ERPConfig(
        base_url=config.base_url,
        username=config.username,
        password=config.password,
        company=config.company,
        timeout=config.timeout,
        max_retries=config.max_retries,
        retry_backoff=config.retry_backoff
    )
    
    if config.adapter_type == "acumatica":
        return AcumaticaAdapter(erp_config)
    elif config.adapter_type == "odoo":
        # Placeholder for Odoo adapter
        # from .odoo.odoo_adapter import OdooAdapter
        # return OdooAdapter(erp_config)
        return None
    else:
        raise ValueError(f"Unsupported ERP adapter type: {config.adapter_type}")



