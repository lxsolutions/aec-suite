

"""
Project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional

from ..dependencies import call_service, get_idempotency_key
from core.config import settings
from core.security import get_current_user
from libs.py.aec_shared.errors import InternalServerError, create_http_exception, ConflictError
from libs.py.aec_shared.otel import get_current_trace_id
from core.idempotency import idempotency_manager, require_idempotency_key, handle_idempotency

router = APIRouter(prefix="/v1/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    client_id: str
    start_date: str
    end_date: Optional[str] = None
    budget: Optional[float] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    client_id: str
    start_date: str
    end_date: Optional[str]
    budget: Optional[float]
    status: str
    created_at: str
    updated_at: str

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(get_current_user)
):
    """List all projects for the organization"""
    try:
        response = await call_service(
            f"{settings.ORCHESTRATOR_URL}/projects",
            headers={"X-Org-ID": current_user["org_id"]}
        )
        return response.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to fetch projects: {str(e)}", trace_id)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create a new project"""
    try:
        # Require idempotency key for create operations
        idempotency_key = await require_idempotency_key(idempotency_key, "project")
        
        # Handle idempotent operation
        async def create_project_operation():
            response = await call_service(
                f"{settings.ORCHESTRATOR_URL}/projects",
                method="post",
                json=project.dict(),
                headers={
                    "X-Org-ID": current_user["org_id"],
                    "Idempotency-Key": idempotency_key
                }
            )
            return response.json()
        
        return await handle_idempotency(
            idempotency_key, "project", create_project_operation
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to create project: {str(e)}", trace_id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get project details"""
    try:
        response = await call_service(
            f"{settings.ORCHESTRATOR_URL}/projects/{project_id}",
            headers={"X-Org-ID": current_user["org_id"]}
        )
        return response.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        trace_id = get_current_trace_id()
        raise InternalServerError(f"Failed to fetch project: {str(e)}", trace_id)

