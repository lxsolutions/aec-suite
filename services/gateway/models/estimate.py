

"""
Estimate database model
"""

from sqlalchemy import Column, String, DateTime, Float, Enum, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
import uuid
from datetime import datetime

from db import Base
from aec_shared.models import EstimateStatus


class Estimate(Base):
    __tablename__ = "estimates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    rfp_id = Column(UUID(as_uuid=True), ForeignKey("rfp_artifacts.id"), nullable=True)
    version = Column(Integer, default=1)
    status = Column(Enum(EstimateStatus), default=EstimateStatus.DRAFT)
    total_amount = Column(Float, default=0.0)
    items = Column(JSON, nullable=True)  # Store estimate items as JSON
    notes = Column(String(500), nullable=True)
    org_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Estimate {self.id} (v{self.version})>"

