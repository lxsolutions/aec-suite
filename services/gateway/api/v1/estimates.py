from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from ..dependencies import get_org_id, get_idempotency_key
from libs.py.aec_shared.errors import InternalServerError, ConflictError
from libs.py.aec_shared.otel import get_current_trace_id
from core.idempotency import idempotency_manager, require_idempotency_key, handle_idempotency

router = APIRouter(prefix="/v1/estimates", tags=["estimates"])

class EstimateItem(BaseModel):
    code: str
    description: str = ""
    uom: str = "ea"
    qty: float = 1.0
    unit_cost: float = 0.0

class Estimate(BaseModel):
    project_id: str
    items: list[EstimateItem] = Field(default_factory=list)
    currency: str = "USD"

class EstimateResponse(BaseModel):
    id: str
    project_id: str
    version: int
    status: str
    total_amount: float
    items: list[EstimateItem]
    created_at: str
    updated_at: str

@router.post("", response_model=Estimate)
async def create_estimate(
    payload: Estimate, 
    org_id: str = Depends(get_org_id),
    idempotency_key: Optional[str] = Depends(get_idempotency_key)
):
    """Create a new estimate"""
    try:
        # Require idempotency key for create operations
        idempotency_key = await require_idempotency_key(idempotency_key, "estimate")
        
        # Handle idempotent operation
        async def create_estimate_operation():
            # TODO: call rover/orchestrator; temporary echo + idempotent placeholder
            return payload
        
        return await handle_idempotency(
            idempotency_key, "estimate", create_estimate_operation
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to create estimate: {str(e)}", trace_id)

@router.post("/rfp:ingest", response_model=Estimate)
async def ingest_rfp(file: UploadFile = File(...), org_id: str = Depends(get_org_id)):
    """Ingest RFP and generate estimate"""
    try:
        # TODO: parse; for now, return a simple stubbed estimate
        return Estimate(project_id="stub-project", items=[EstimateItem(code="DIV01", description=file.filename, qty=1, unit_cost=1000)])
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to ingest RFP: {str(e)}", trace_id)

@router.get("", response_model=List[EstimateResponse])
async def get_estimates(
    project_id: Optional[str] = Query(None, description="Filter estimates by project ID"),
    org_id: str = Depends(get_org_id)
):
    """Get estimates, optionally filtered by project ID"""
    try:
        # TODO: call rover/orchestrator to get actual estimates
        # For now, return mock data for testing
        if project_id:
            return [
                EstimateResponse(
                    id="test-estimate-001",
                    project_id=project_id,
                    version=1,
                    status="draft",
                    total_amount=50000.0,
                    items=[
                        EstimateItem(
                            code="DIV01",
                            description="Excavation",
                            uom="cy",
                            qty=100.0,
                            unit_cost=25.0
                        )
                    ],
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-01T00:00:00Z"
                )
            ]
        else:
            # Return empty list if no project_id provided
            return []
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to retrieve estimates: {str(e)}", trace_id)
