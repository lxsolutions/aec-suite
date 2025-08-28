


from sqlalchemy.orm import Session
from typing import List
import yaml
import os
from datetime import datetime

from ..models import Estimate, EstimateLine, ComplianceFinding, RFP
from ..schemas import EstimateCreate, EstimateLineCreate
from .rfp_service import get_rfp_by_id

# Path to cost templates
COST_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "data", "cost_templates")

async def create_estimate_from_findings(db: Session, estimate_data: EstimateCreate) -> Estimate:
    """Create estimate from compliance findings"""
    
    rfp = get_rfp_by_id(db, estimate_data.rfp_id)
    
    # Load cost templates
    cost_templates = load_cost_templates()
    
    # Create estimate
    estimate = Estimate(
        rfp_id=rfp.id,
        name=estimate_data.name,
        description=estimate_data.description,
        location_factor=estimate_data.location_factor,
        status="draft"
    )
    
    db.add(estimate)
    db.commit()
    db.refresh(estimate)
    
    # Get compliance findings for this RFP
    findings = db.query(ComplianceFinding).filter(ComplianceFinding.rfp_id == rfp.id).all()
    
    # Create estimate lines from findings
    estimate_lines = []
    total_amount = 0.0
    
    for finding in findings:
        # Map finding to cost template
        cost_line = map_finding_to_cost(finding, cost_templates)
        if cost_line:
            # Apply location factor
            unit_cost = cost_line['unit_cost'] * estimate_data.location_factor
            total_cost = unit_cost * cost_line['quantity']
            
            estimate_line = EstimateLine(
                estimate_id=estimate.id,
                finding_id=finding.id,
                csi_code=cost_line['csi_code'],
                description=cost_line['description'],
                unit=cost_line['unit'],
                quantity=cost_line['quantity'],
                unit_cost=unit_cost,
                total_cost=total_cost,
                is_custom=False
            )
            
            estimate_lines.append(estimate_line)
            total_amount += total_cost
    
    # Add custom lines from request
    for line_data in estimate_data.lines:
        unit_cost = line_data.unit_cost * estimate_data.location_factor
        total_cost = unit_cost * line_data.quantity
        
        estimate_line = EstimateLine(
            estimate_id=estimate.id,
            csi_code=line_data.csi_code,
            description=line_data.description,
            unit=line_data.unit,
            quantity=line_data.quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            is_custom=True,
            notes=line_data.notes
        )
        
        estimate_lines.append(estimate_line)
        total_amount += total_cost
    
    # Add all lines to database
    db.add_all(estimate_lines)
    
    # Update estimate total
    estimate.total_amount = total_amount
    db.commit()
    db.refresh(estimate)
    
    return estimate

def load_cost_templates() -> dict:
    """Load cost templates from YAML files"""
    templates = {}
    
    for filename in os.listdir(COST_TEMPLATES_DIR):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            template_name = filename.replace('.yaml', '').replace('.yml', '')
            template_file = os.path.join(COST_TEMPLATES_DIR, filename)
            
            try:
                with open(template_file, 'r') as f:
                    templates[template_name] = yaml.safe_load(f)
            except Exception as e:
                print(f"Warning: Failed to load cost template {filename}: {str(e)}")
    
    return templates

def map_finding_to_cost(finding: ComplianceFinding, cost_templates: dict) -> dict:
    """Map compliance finding to cost template"""
    # Simple mapping logic - in real implementation, this would be more sophisticated
    # using rule_id to CSI code mapping or ML-based classification
    
    # For now, use a simple mapping based on rule category
    category_mapping = {
        'code': {'csi_code': '01 50 00', 'description': 'Code Compliance Work', 'unit': 'hour', 'quantity': 8.0, 'unit_cost': 125.0},
        'brand': {'csi_code': '01 60 00', 'description': 'Brand Standard Compliance', 'unit': 'hour', 'quantity': 4.0, 'unit_cost': 95.0},
        'insurance': {'csi_code': '01 70 00', 'description': 'Insurance Compliance', 'unit': 'hour', 'quantity': 2.0, 'unit_cost': 85.0},
        'bonds': {'csi_code': '01 80 00', 'description': 'Bond Compliance', 'unit': 'hour', 'quantity': 3.0, 'unit_cost': 110.0},
        'alternates': {'csi_code': '01 90 00', 'description': 'Alternate Pricing', 'unit': 'lump_sum', 'quantity': 1.0, 'unit_cost': 500.0},
        'deadlines': {'csi_code': '01 25 00', 'description': 'Expedited Work', 'unit': 'hour', 'quantity': 10.0, 'unit_cost': 150.0},
        'ada_fha': {'csi_code': '01 55 00', 'description': 'Accessibility Compliance', 'unit': 'hour', 'quantity': 6.0, 'unit_cost': 135.0}
    }
    
    return category_mapping.get(finding.rule_category, None)

def get_estimate_by_id(db: Session, estimate_id: str) -> Estimate:
    """Get estimate by ID"""
    estimate = db.query(Estimate).filter(Estimate.id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return estimate


