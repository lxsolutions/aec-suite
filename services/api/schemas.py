

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class RFPUpload(BaseModel):
    project_id: Optional[str] = None
    filename: str
    file_size: int
    mime_type: str

class RFPResponse(BaseModel):
    id: uuid.UUID
    project_id: Optional[str] = None
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplianceFindingResponse(BaseModel):
    id: uuid.UUID
    rule_id: str
    rule_category: str
    severity: str
    description: str
    citation_text: str
    citation_start: Optional[int] = None
    citation_end: Optional[int] = None
    suggested_fix: Optional[str] = None
    ruleset_version: str
    is_llm_generated: bool
    confidence_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EstimateLineCreate(BaseModel):
    csi_code: str
    description: str
    unit: str
    quantity: float = Field(gt=0)
    unit_cost: float = Field(gt=0)
    notes: Optional[str] = None

class EstimateCreate(BaseModel):
    rfp_id: uuid.UUID
    name: str
    description: Optional[str] = None
    location_factor: float = Field(gt=0, default=1.0)
    lines: List[EstimateLineCreate] = Field(min_items=1)

class EstimateLineResponse(BaseModel):
    id: uuid.UUID
    csi_code: str
    description: str
    unit: str
    quantity: float
    unit_cost: float
    total_cost: float
    is_custom: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EstimateResponse(BaseModel):
    id: uuid.UUID
    rfp_id: uuid.UUID
    name: str
    description: Optional[str] = None
    status: str
    total_amount: float
    currency: str
    location_factor: float
    lines: List[EstimateLineResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str

