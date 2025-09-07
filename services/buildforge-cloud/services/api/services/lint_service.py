


from sqlalchemy.orm import Session
from typing import List, Optional
import yaml
import os
import re
from datetime import datetime

from ..models import RFP, ComplianceFinding
from .rfp_service import get_rfp_by_id

# Path to rulepacks
RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "data", "spec_rules")

async def lint_rfp(db: Session, rfp_id: str, ruleset_version: Optional[str] = None) -> List[ComplianceFinding]:
    """Lint RFP against compliance rules"""
    
    rfp = get_rfp_by_id(db, rfp_id)
    
    if not rfp.extracted_text:
        raise HTTPException(status_code=400, detail="No text extracted from RFP")
    
    # Load rules
    rules = load_rules(ruleset_version)
    
    findings = []
    
    # Run deterministic checks
    findings.extend(run_deterministic_checks(rfp.extracted_text, rules))
    
    # TODO: Add LLM fallback for complex checks
    # findings.extend(await run_llm_checks(rfp.extracted_text, rules))
    
    # Save findings to database
    for finding_data in findings:
        finding = ComplianceFinding(
            rfp_id=rfp.id,
            **finding_data
        )
        db.add(finding)
    
    db.commit()
    
    return db.query(ComplianceFinding).filter(ComplianceFinding.rfp_id == rfp.id).all()

def load_rules(ruleset_version: Optional[str] = None) -> dict:
    """Load compliance rules from YAML files"""
    rules = {}
    
    # Default to latest version if not specified
    if not ruleset_version:
        # Find latest version
        versions = []
        for filename in os.listdir(RULES_DIR):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                versions.append(filename.replace('.yaml', '').replace('.yml', ''))
        
        if not versions:
            raise HTTPException(status_code=500, detail="No rulepacks found")
        
        ruleset_version = sorted(versions)[-1]  # Get latest version
    
    rule_file = os.path.join(RULES_DIR, f"{ruleset_version}.yaml")
    
    if not os.path.exists(rule_file):
        raise HTTPException(status_code=404, detail=f"Ruleset version {ruleset_version} not found")
    
    try:
        with open(rule_file, 'r') as f:
            rules = yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load rules: {str(e)}")
    
    return rules

def run_deterministic_checks(text: str, rules: dict) -> List[dict]:
    """Run deterministic pattern-based checks"""
    findings = []
    
    for category, category_rules in rules.get('categories', {}).items():
        for rule_id, rule in category_rules.get('rules', {}).items():
            if rule.get('type') == 'pattern':
                findings.extend(check_pattern_rule(text, rule_id, category, rule))
            elif rule.get('type') == 'required':
                findings.extend(check_required_rule(text, rule_id, category, rule))
    
    return findings

def check_pattern_rule(text: str, rule_id: str, category: str, rule: dict) -> List[dict]:
    """Check pattern-based rules"""
    findings = []
    patterns = rule.get('patterns', [])
    severity = rule.get('severity', 'medium')
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            findings.append({
                'rule_id': rule_id,
                'rule_category': category,
                'severity': severity,
                'description': rule.get('description', ''),
                'citation_text': match.group(0),
                'citation_start': match.start(),
                'citation_end': match.end(),
                'suggested_fix': rule.get('suggested_fix'),
                'ruleset_version': rule.get('version', '1.0'),
                'is_llm_generated': False,
                'confidence_score': 1.0
            })
    
    return findings

def check_required_rule(text: str, rule_id: str, category: str, rule: dict) -> List[dict]:
    """Check required content rules"""
    findings = []
    required_terms = rule.get('required_terms', [])
    severity = rule.get('severity', 'high')
    
    missing_terms = []
    for term in required_terms:
        if not re.search(term, text, re.IGNORECASE):
            missing_terms.append(term)
    
    if missing_terms:
        findings.append({
            'rule_id': rule_id,
            'rule_category': category,
            'severity': severity,
            'description': f"Missing required terms: {', '.join(missing_terms)}",
            'citation_text': "",
            'citation_start': None,
            'citation_end': None,
            'suggested_fix': rule.get('suggested_fix', f"Include the missing terms: {', '.join(missing_terms)}"),
            'ruleset_version': rule.get('version', '1.0'),
            'is_llm_generated': False,
            'confidence_score': 1.0
        })
    
    return findings

# TODO: Implement LLM-based checks
async def run_llm_checks(text: str, rules: dict) -> List[dict]:
    """Run LLM-based checks for complex compliance validation"""
    # This would integrate with an LLM service for complex rule checking
    # For now, return empty list
    return []


