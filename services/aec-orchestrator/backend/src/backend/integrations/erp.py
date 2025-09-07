





from datetime import datetime

# Mock Acumatica/Odoo API integration

def sync_financial_data():
    """Mock financial data synchronization from ERP systems."""

    # Simulate data from Acumatica
    acumatica_data = {
        "revenue": 1250000.75,
        "expenses": 987654.32,
        "profit_margin": 0.23,
        "accounts_payable": 150000.00,
        "accounts_receivable": 210000.00
    }

    # Simulate data from Odoo
    odoo_data = {
        "inventory_value": 876345.98,
        "cost_of_goods_sold": 654321.12,
        "gross_profit": 400000.66
    }

    # Combine and normalize data
    combined_data = {
        "source": ["Acumatica", "Odoo"],
        "financials": {
            **acumatica_data,
            "inventory_value": odoo_data["inventory_value"],
            "cost_of_goods_sold": odoo_data["cost_of_goods_sold"]
        },
        "sync_status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

    return combined_data

def sync_inventory():
    """Mock inventory synchronization from ERP systems."""

    # Simulate inventory data
    mock_items = [
        {"item_id": "WID-234", "description": "Wooden beams", "quantity": 10, "location": "Warehouse A"},
        {"item_id": "STL-567", "description": "Steel columns", "quantity": 8, "location": "Yard B"},
        {"item_id": "GLA-890", "description": "Glass panels", "quantity": 25, "location": "Warehouse C"}
    ]

    return {
        "inventory_items": mock_items,
        "total_items": len(mock_items),
        "sync_status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # Example usage
    financial_data = sync_financial_data()
    inventory_data = sync_inventory()

    print("Financial Data:", financial_data)
    print("Inventory Data:", inventory_data)


