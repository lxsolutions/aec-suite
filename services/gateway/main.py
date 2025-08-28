
#!/usr/bin/env python3
"""
AEC Suite API Gateway - FastAPI implementation
Main entry point for the gateway service
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .core.config import settings
from .core.security import get_current_user
from .api.v1 import projects, rfps, estimates, schedules, erp, health
from .core.events import nats_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management"""
    # Startup
    logger.info("Starting AEC Gateway service")
    
    # Initialize NATS connection
    await nats_client.connect()
    logger.info("NATS client connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AEC Gateway service")
    await nats_client.close()

def configure_tracing() -> None:
    """Configure OpenTelemetry tracing"""
    resource = Resource.create(attributes={"service.name": "aec-gateway"})
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER_HOST,
        agent_port=settings.JAEGER_PORT,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Configure tracing if enabled
    if settings.ENABLE_TRACING:
        configure_tracing()
    
    app = FastAPI(
        title="AEC Suite API Gateway",
        description="Unified API gateway for AEC Suite services",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    
    # Instrument with OpenTelemetry
    if settings.ENABLE_TRACING:
        FastAPIInstrumentor.instrument_app(app)
    
    # Include routers
    app.include_router(health.router, prefix="/healthz", tags=["health"])
    app.include_router(projects.router, prefix="/v1/projects", tags=["projects"])
    app.include_router(rfps.router, prefix="/v1/rfps", tags=["rfps"])
    app.include_router(estimates.router, prefix="/v1/estimates", tags=["estimates"])
    app.include_router(schedules.router, prefix="/v1/schedules", tags=["schedules"])
    app.include_router(erp.router, prefix="/v1/erp", tags=["erp"])
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
