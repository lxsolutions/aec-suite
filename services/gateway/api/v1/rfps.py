


"""
RFP (Request for Proposal) management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional

from ..dependencies import call_service
from core.config import settings
from core.security import get_current_user
from core.events import nats_client

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch RFPs: {str(e)}"
        )

@router.post("", response_model=RFPResponse, status_code=status.HTTP_201_CREATED)
async def create_rfp(
    rfp: RFPCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new RFP"""
    try:
        response = await call_service(
            f"{settings.BUILDFORGE_URL}/rfps",
            method="post",
            json=rfp.dict(),
            headers={"X-Org-ID": current_user["org_id"]}
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
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create RFP: {str(e)}"
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


