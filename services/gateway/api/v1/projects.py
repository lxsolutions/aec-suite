

"""
Project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from ..dependencies import call_service
from core.config import settings
from core.security import get_current_user

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    try:
        response = await call_service(
            f"{settings.ORCHESTRATOR_URL}/projects",
            method="post",
            json=project.dict(),
            headers={"X-Org-ID": current_user["org_id"]}
        )
        return response.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )

