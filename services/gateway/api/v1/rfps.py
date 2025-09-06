


"""
RFP (Request for Proposal) management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Header
from pydantic import BaseModel
from typing import List, Optional

from ..dependencies import call_service
from core.config import settings
from core.security import get_current_user
from core.events import nats_client
from libs.py.aec_shared.errors import InternalServerError, ConflictError
from libs.py.aec_shared.otel import get_current_trace_id
from core.idempotency import idempotency_manager, require_idempotency_key, handle_idempotency

router = APIRouter(prefix="/v1/rfps", tags=["rfps"])

class RFPCreate(BaseModel):
    project_id: str
    title: str
    description: str
    due_date: str
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None
    requirements: List[str] = []

class RFPResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    due_date: str
    budget_range_min: Optional[float]
    budget_range_max: Optional[float]
    requirements: List[str]
    status: str
    created_at: str
    updated_at: str

@router.get("", response_model=List[RFPResponse])
async def list_rfps(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List RFPs, optionally filtered by project"""
    try:
        url = f"{settings.BUILDFORGE_URL}/rfps"
        if project_id:
            url += f"?project_id={project_id}"
        
        response = await call_service(
            url,
            headers={"X-Org-ID": current_user["org_id"]}
        )
        return response.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to fetch RFPs: {str(e)}", trace_id)

@router.post("", response_model=RFPResponse, status_code=status.HTTP_201_CREATED)
async def create_rfp(
    rfp: RFPCreate,
    current_user: dict = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create a new RFP"""
    try:
        # Require idempotency key for create operations
        idempotency_key = await require_idempotency_key(idempotency_key, "rfp")
        
        # Handle idempotent operation
        async def create_rfp_operation():
            response = await call_service(
                f"{settings.BUILDFORGE_URL}/rfps",
                method="post",
                json=rfp.dict(),
                headers={
                    "X-Org-ID": current_user["org_id"],
                    "Idempotency-Key": idempotency_key
                }
            )
            
            # Publish RFP created event
            rfp_data = response.json()
            await nats_client.publish(
                "rfp.created",
                {
                    "rfp_id": rfp_data["id"],
                    "project_id": rfp_data["project_id"],
                    "org_id": current_user["org_id"],
                    "due_date": rfp_data["due_date"]
                }
            )
            
            return rfp_data
        
        return await handle_idempotency(
            idempotency_key, "rfp", create_rfp_operation
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to create RFP: {str(e)}", trace_id)

@router.post("/{rfp_id}/documents")
async def upload_rfp_document(
    rfp_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload document for RFP"""
    try:
        files = {"file": (file.filename, file.file, file.content_type)}
        response = await call_service(
            f"{settings.BUILDFORGE_URL}/rfps/{rfp_id}/documents",
            method="post",
            files=files,
            headers={"X-Org-ID": current_user["org_id"]}
        )
        return response.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to upload document: {str(e)}", trace_id)

@router.post("/ingest", response_model=RFPResponse)
async def ingest_rfp(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Ingest RFP document and trigger parsing"""
    try:
        # Save file and trigger orchestrator
        files = {"file": (file.filename, file.file, file.content_type)}
        data = {"project_id": project_id}
        
        response = await call_service(
            f"{settings.ORCHESTRATOR_URL}/rfps/ingest",
            method="post",
            files=files,
            data=data,
            headers={"X-Org-ID": current_user["org_id"]}
        )
        
        # Publish RFP parsed event
        rfp_data = response.json()
        await nats_client.publish(
            "rfp.parsed",
            {
                "rfp_id": rfp_data["id"],
                "project_id": project_id,
                "org_id": current_user["org_id"],
                "filename": file.filename
            }
        )
        
        return rfp_data
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to ingest RFP: {str(e)}", trace_id)


