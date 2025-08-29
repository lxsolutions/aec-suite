
"""
Shared domain models for AEC Suite
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RfpStatus(str, Enum):
    RECEIVED = "received"
    PARSING = "parsing"
    PARSED = "parsed"
    ERROR = "error"


class EstimateStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    READY = "ready"
    APPROVED = "approved"
    SYNCED = "synced"


class ScheduleStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    client_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    org_id: str

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Rfp(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: RfpStatus = RfpStatus.RECEIVED
    parsed_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    org_id: str

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class EstimateItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    description: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float
    category: str
    notes: Optional[str] = None

    @validator('total_cost', always=True)
    def calculate_total_cost(cls, v, values):
        if v is None:
            return values['quantity'] * values['unit_cost']
        return v

    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: lambda v: str(v)
        }


class Estimate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    rfp_id: UUID
    version: int = 1
    status: EstimateStatus = EstimateStatus.DRAFT
    total_amount: float = 0.0
    items: List[EstimateItem] = []
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    org_id: str

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Schedule(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    estimate_id: UUID
    start_date: datetime
    end_date: datetime
    status: ScheduleStatus = ScheduleStatus.DRAFT
    milestones: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    org_id: str

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
