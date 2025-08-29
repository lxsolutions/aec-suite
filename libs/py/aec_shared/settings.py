


"""
Shared settings and configuration for AEC Suite
"""

from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn, AnyUrl
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://aec:aec123@localhost:5432/aec_suite",
        description="PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database connection max overflow")
    DATABASE_ECHO: bool = Field(default=False, description="Enable SQL query logging")


class NATSSettings(BaseSettings):
    """NATS configuration"""
    NATS_URL: str = Field(
        default="nats://localhost:4222",
        description="NATS server connection URL"
    )
    NATS_STREAM_NAME: str = Field(default="aec_events", description="NATS JetStream stream name")
    NATS_SUBJECT_PREFIX: str = Field(default="aec", description="NATS subject prefix")


class RedisSettings(BaseSettings):
    """Redis configuration"""
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")


class OpenTelemetrySettings(BaseSettings):
    """OpenTelemetry configuration"""
    ENABLE_TRACING: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    JAEGER_HOST: str = Field(default="localhost", description="Jaeger agent host")
    JAEGER_PORT: int = Field(default=6831, description="Jaeger agent port")
    OTLP_ENDPOINT: Optional[str] = Field(default=None, description="OTLP endpoint URL")


class JWTSettings(BaseSettings):
    """JWT configuration"""
    JWT_SECRET: str = Field(
        default="your-super-secret-jwt-key-here-change-in-production",
        description="JWT secret key for token signing"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )


class CORSSettings(BaseSettings):
    """CORS configuration"""
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"], description="Allowed CORS methods")
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"], description="Allowed CORS headers")


class ServiceSettings(BaseSettings):
    """Service endpoint configuration"""
    ORCHESTRATOR_URL: AnyUrl = Field(
        default="http://localhost:8000",
        description="Orchestrator service URL"
    )
    ROVER_URL: AnyUrl = Field(
        default="http://localhost:3000",
        description="Rover service URL"
    )
    ERP_BRIDGE_URL: AnyUrl = Field(
        default="http://localhost:4000",
        description="ERP Bridge service URL"
    )
    BUILDFORGE_URL: AnyUrl = Field(
        default="http://localhost:5000",
        description="BuildForge service URL"
    )


class AppSettings(BaseSettings):
    """Main application settings"""
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    HOST: str = Field(default="0.0.0.0", description="Application host")
    PORT: int = Field(default=8080, description="Application port")
    ALLOWED_HOSTS: list[str] = Field(default=["*"], description="Allowed hosts")
    
    # Nested settings
    database: DatabaseSettings = DatabaseSettings()
    nats: NATSSettings = NATSSettings()
    redis: RedisSettings = RedisSettings()
    otel: OpenTelemetrySettings = OpenTelemetrySettings()
    jwt: JWTSettings = JWTSettings()
    cors: CORSSettings = CORSSettings()
    services: ServiceSettings = ServiceSettings()
    
    class Config:
        env_prefix = "AEC_"
        case_sensitive = False
        env_nested_delimiter = "__"


# Global settings instance
settings = AppSettings()

