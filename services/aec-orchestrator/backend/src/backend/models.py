

from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Table, Boolean, Float, create_engine, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Role enumeration for RBAC
class UserRole(PyEnum):
    OWNER = "owner"
    ADMIN = "admin" 
    PM = "project_manager"
    FIELD = "field_technician"

# Organization model for multi-tenancy
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100), nullable=False, unique=True)
    slug = Column(String(length=50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# User model for authentication with RBAC
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    is_verified = Column(Boolean(), default=False, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FIELD, nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", backref="users")

# Project table with organization relationship
class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", backref="projects")

# Estimate model for AEC estimating
class Estimate(Base):
    __tablename__ = "estimates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(length=200), nullable=False)
    description = Column(String(length=500), nullable=True)
    
    # Financial totals
    material_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    equipment_cost = Column(Float, default=0.0)
    subcontractor_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Status and metadata
    status = Column(String(length=20), default="draft")  # draft, submitted, approved, rejected
    version = Column(Integer, default=1)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", backref="estimates")
    organization = relationship("Organization", backref="estimates")
    creator = relationship("User", foreign_keys=[created_by], backref="created_estimates")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_estimates")
    rejector = relationship("User", foreign_keys=[rejected_by], backref="rejected_estimates")

# AgentRun table with organization relationship
class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    agent_type = Column(String(length=50), nullable=False)
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    status = Column(String(length=20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", backref="agent_runs")

# KnowledgeBase table for vector embeddings with organization relationship
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    embedding = Column(JSONB, nullable=False)  # Vector embedding (using JSONB for simplicity)
    content_type = Column(String(length=50), nullable=False)
    doc_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", backref="knowledge_base")

# Agent table for different agent types with organization relationship
class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(length=100), nullable=False)
    type = Column(String(length=50), nullable=False)
    description = Column(String(length=255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", backref="agents")

