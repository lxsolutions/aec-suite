


"""
Project database model
"""

from sqlalchemy import Column, String, DateTime, Float, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from db import Base
from aec_shared.models import ProjectStatus


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    client_id = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    budget = Column(Float, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    org_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Project {self.name} ({self.status})>"


