

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyUserTableUUID

class User(SQLAlchemyUserTableUUID):
    pass

class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    data = Column(JSON)

class AgentRun(Base):
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id"))
    output = Column(JSON)

class KnowledgeBase(Base):
    id = Column(Integer, primary_key=True, index=True)
    embedding_vector = Column(Vector)  # PGVector

