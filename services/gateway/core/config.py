

"""
Configuration settings for AEC Gateway service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: List[str] = ["localhost", "0.0.0.0", "127.0.0.1"]
    
    # Database
    DATABASE_URL: str = "postgresql://aec:aec123@localhost:5432/aec_suite"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # NATS
    NATS_URL: str = "nats://localhost:4222"
    
    # Services
    ORCHESTRATOR_URL: str = "http://localhost:8001"
    ROVER_URL: str = "http://localhost:8002"
    ERP_BRIDGE_URL: str = "http://localhost:8003"
    BUILDFORGE_URL: str = "http://localhost:8004"
    
    # Observability
    ENABLE_TRACING: bool = True
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831
    
    # File storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()


