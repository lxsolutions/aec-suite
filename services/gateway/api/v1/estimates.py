from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from ..dependencies import get_org_id

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

@router.post("", response_model=Estimate)
async def create_estimate(payload: Estimate, org_id: str = Depends(get_org_id)):
    # TODO: call rover/orchestrator; temporary echo + idempotent placeholder
    return payload

@router.post("/rfp:ingest", response_model=Estimate)
async def ingest_rfp(file: UploadFile = File(...), org_id: str = Depends(get_org_id)):
    # TODO: parse; for now, return a simple stubbed estimate
    return Estimate(project_id="stub-project", items=[EstimateItem(code="DIV01", description=file.filename, qty=1, unit_cost=1000)])
