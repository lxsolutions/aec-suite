

from datetime import datetime
from typing import Optional, List

import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Table, Boolean, Float, create_engine
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# User model for authentication
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    is_verified = Column(Boolean(), default=False, nullable=False)

# Project table
class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100), nullable=False)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# AgentRun table
class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    agent_type = Column(String(length=50), nullable=False)
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    status = Column(String(length=20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# KnowledgeBase table for vector embeddings
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    embedding = Column(JSONB, nullable=False)  # Vector embedding (using JSONB for simplicity)
    content_type = Column(String(length=50), nullable=False)
    doc_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Agent table for different agent types
class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100), nullable=False)
    type = Column(String(length=50), nullable=False)
    description = Column(String(length=255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

