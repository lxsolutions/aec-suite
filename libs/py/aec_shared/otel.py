

"""
OpenTelemetry utilities for AEC Suite
"""

import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


logger = logging.getLogger(__name__)


def configure_tracing(
    service_name: str,
    jaeger_host: Optional[str] = None,
    jaeger_port: int = 6831,
    otlp_endpoint: Optional[str] = None,
    enable_console: bool = False
) -> None:
    """
    Configure OpenTelemetry tracing
    
    Args:
        service_name: Name of the service for tracing
        jaeger_host: Jaeger agent host (optional)
        jaeger_port: Jaeger agent port (default: 6831)
        otlp_endpoint: OTLP endpoint URL (optional)
        enable_console: Whether to enable console exporter for debugging
    """
    resource = Resource.create({SERVICE_NAME: service_name})
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Add exporters based on configuration
    if jaeger_host:
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        logger.info(f"Configured Jaeger exporter for {service_name}")
    
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"Configured OTLP exporter for {service_name}")
    
    if enable_console:
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info(f"Configured console exporter for {service_name}")
    
    # Auto-instrument HTTP clients
    RequestsInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    
    logger.info(f"Tracing configured for {service_name}")


def instrument_fastapi(app, service_name: str) -> None:
    """Instrument FastAPI application with OpenTelemetry"""
    FastAPIInstrumentor.instrument_app(app)
    logger.info(f"FastAPI application {service_name} instrumented with OpenTelemetry")


def get_tracer(service_name: str) -> trace.Tracer:
    """Get a tracer for the specified service"""
    return trace.get_tracer(service_name)


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID from context"""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


def get_current_span_id() -> Optional[str]:
    """Get the current span ID from context"""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return None

