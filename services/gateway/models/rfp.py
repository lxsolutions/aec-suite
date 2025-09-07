


"""
RFP Artifact database model
"""

from sqlalchemy import Column, String, DateTime, Integer, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
import uuid
from datetime import datetime

from db import Base
from aec_shared.models import RfpStatus


class RfpArtifact(Base):
    __tablename__ = "rfp_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(Enum(RfpStatus), default=RfpStatus.RECEIVED)
    parsed_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    org_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RfpArtifact {self.filename} ({self.status})>"


