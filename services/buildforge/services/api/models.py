


from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .database import Base

class RFP(Base):
    __tablename__ = "rfps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    text_hash = Column(String, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    findings = relationship("ComplianceFinding", back_populates="rfp", cascade="all, delete-orphan")
    estimates = relationship("Estimate", back_populates="rfp", cascade="all, delete-orphan")

class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfp_id = Column(UUID(as_uuid=True), ForeignKey("rfps.id"), nullable=False)
    rule_id = Column(String, nullable=False)
    rule_category = Column(String, nullable=False)  # code, brand, insurance, bonds, alternates, deadlines, ada_fha
    severity = Column(String, nullable=False)  # critical, high, medium, low, info
    description = Column(Text, nullable=False)
    citation_text = Column(Text, nullable=False)
    citation_start = Column(Integer, nullable=True)
    citation_end = Column(Integer, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    ruleset_version = Column(String, nullable=False)
    is_llm_generated = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    rfp = relationship("RFP", back_populates="findings")
    estimate_lines = relationship("EstimateLine", back_populates="finding")

class Estimate(Base):
    __tablename__ = "estimates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfp_id = Column(UUID(as_uuid=True), ForeignKey("rfps.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft, submitted, approved, rejected
    total_amount = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    location_factor = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rfp = relationship("RFP", back_populates="estimates")
    lines = relationship("EstimateLine", back_populates="estimate", cascade="all, delete-orphan")

class EstimateLine(Base):
    __tablename__ = "estimate_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estimate_id = Column(UUID(as_uuid=True), ForeignKey("estimates.id"), nullable=False)
    finding_id = Column(UUID(as_uuid=True), ForeignKey("compliance_findings.id"), nullable=True)
    csi_code = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    unit = Column(String, nullable=False)  # each, sqft, lf, hour, etc.
    quantity = Column(Float, default=1.0)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    is_custom = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    estimate = relationship("Estimate", back_populates="lines")
    finding = relationship("ComplianceFinding", back_populates="estimate_lines")


