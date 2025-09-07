
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

from core.config import settings
from core.security import get_current_user
from api.v1 import projects, rfps, estimates, health
from api.dependencies import get_service_health
from core.events import nats_client
from core.middleware.rate_limit import (
    create_rate_limit_middleware, 
    rate_limit_exceeded_handler,
    limiter,
    RateLimitExceeded
)
from core.middleware.error_handler import create_error_handler_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management"""
    # Startup
    logger.info("Starting AEC Gateway service")
    
    # Initialize NATS connection with timeout (optional for now)
    try:
        import asyncio
        await asyncio.wait_for(nats_client.connect(), timeout=5.0)
        logger.info("NATS client connected")
    except asyncio.TimeoutError:
        logger.warning("NATS connection timed out after 5 seconds. Continuing without NATS.")
    except Exception as e:
        logger.warning(f"NATS connection failed: {e}. Continuing without NATS.")
    
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
    
    # Rate limiting middleware
    rate_limit_middleware = create_rate_limit_middleware()
    if rate_limit_middleware:
        app.add_middleware(rate_limit_middleware)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # Error handling middleware
    error_handler_middleware = create_error_handler_middleware()
    app.add_middleware(error_handler_middleware)
    
    # Instrument with OpenTelemetry
    if settings.ENABLE_TRACING:
        FastAPIInstrumentor.instrument_app(app)
    
    # Add standalone health endpoints for Kubernetes
    @app.get("/healthz")
    async def healthz():
        """Kubernetes health check endpoint"""
        return {"status": "ok"}

    @app.get("/readyz")  
    async def readyz():
        """Kubernetes readiness check endpoint"""
        # For testing purposes, always return ready
        # In production, this would check actual service health
        return {"status": "ready"}

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(projects.router, tags=["projects"])
    app.include_router(rfps.router, tags=["rfps"])
    app.include_router(estimates.router, tags=["estimates"])
    # app.include_router(schedules.router, prefix="/v1/schedules", tags=["schedules"])
    # app.include_router(erp.router, prefix="/v1/erp", tags=["erp"])
    
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
