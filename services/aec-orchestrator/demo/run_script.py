







#!/usr/bin/env python3
"""
Sample script to demonstrate AEC Orchestrator workflow execution.
This script triggers the agent workflow with sample data and prints results.
"""

import requests
import json
from time import sleep

def run_agent_workflow():
    """Run the full agent workflow via API."""

    # Base URL for the backend API (adjust if needed)
    base_url = "http://localhost:8000/api"

    print("Starting AEC Orchestrator workflow...")

    # Step 1: Run bidding agent
    print("\n1. Running Bidding Agent...")
    bidding_response = requests.post(f"{base_url}/agents/run", json={
        "agent_type": "bidding",
        "input_data": {
            "rfp_path": "/workspace/aec-orchestrator/demo/rfp/sample_rfp.txt"
        }
    })

    if bidding_response.status_code == 200:
        print("✓ Bidding agent completed successfully")
        bidding_result = bidding_response.json()
        cost_estimate = bidding_result.get('output_data', {}).get('cost_estimates', [])
        print(f"   Estimated project cost: ${sum(float(est['total']) for est in cost_estimate):,.2f}")
    else:
        print("✗ Bidding agent failed")
        return

    # Step 2: Run design agent
    print("\n2. Running Design Agent...")
    design_response = requests.post(f"{base_url}/agents/run", json={
        "agent_type": "design",
        "input_data": {
            "ifc_path": "/workspace/aec-orchestrator/demo/sample.ifc"
        }
    })

    if design_response.status_code == 200:
        print("✓ Design agent completed successfully")
        design_result = design_response.json()
        sustainability_analysis = design_result.get('output_data', {}).get('sustainability_analysis')
        print(f"   Sustainability recommendations: {len(sustainability_analysis)} items")
    else:
        print("✗ Design agent failed")
        return

    # Step 3: Run schedule agent
    print("\n3. Running Schedule Agent...")
    schedule_response = requests.post(f"{base_url}/agents/run", json={
        "agent_type": "schedule",
        "input_data": {
            "project_tasks": {
                "Foundation": {"duration_days": 30},
                "Structure": {"duration_days": 45, "dependencies": ["Foundation"]},
                "Interiors": {"duration_days": 60, "dependencies": ["Structure"]}
            }
        }
    })

    if schedule_response.status_code == 200:
        print("✓ Schedule agent completed successfully")
        schedule_result = schedule_response.json()
        gantt_data = schedule_result.get('output_data', {}).get('gantt_chart')
        total_duration = schedule_result.get('output_data', {}).get('total_project_duration_days')
        print(f"   Total project duration: {total_duration} days")
    else:
        print("✗ Schedule agent failed")
        return

    # Step 4: Run compliance agent
    print("\n4. Running Compliance Agent...")
    compliance_response = requests.post(f"{base_url}/agents/run", json={
        "agent_type": "compliance",
        "input_data": {
            "query": "ISO 19650 and LEED certification requirements"
        }
    })

    if compliance_response.status_code == 200:
        print("✓ Compliance agent completed successfully")
        compliance_result = compliance_response.json()
        checks = compliance_result.get('output_data', {}).get('compliance_checks')
        print(f"   Found {len(checks)} relevant compliance documents")
    else:
        print("✗ Compliance agent failed")
        return

    # Step 5: Run maintenance agent
    print("\n5. Running Maintenance Agent...")
    maintenance_response = requests.post(f"{base_url}/agents/run", json={
        "agent_type": "maintenance",
        "input_data": {
            "sensor_readings": {
                "temperature": [20.5, 21.3, 19.8],
                "humidity": [45, 50, 47],
                "structural_integrity": [96.2, 95.8, 96.0]
            }
        }
    })

    if maintenance_response.status_code == 200:
        print("✓ Maintenance agent completed successfully")
        maintenance_result = maintenance_response.json()
        alerts = maintenance_result.get('output_data', {}).get('alerts')
        needs = maintenance_result.get('output_data', {}).get('maintenance_needs')
        print(f"   Found {len(alerts)} sensor alerts and {len(needs)} maintenance actions")
    else:
        print("✗ Maintenance agent failed")

    # Summary
    print("\n" + "="*60)
    print("WORKFLOW COMPLETED SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    run_agent_workflow()



