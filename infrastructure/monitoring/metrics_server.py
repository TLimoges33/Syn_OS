"""
SynOS Metrics Server
FastAPI server for exposing performance metrics and health endpoints
"""

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
import asyncio
import logging
from typing import Dict, Any
import uvicorn

from performance_monitor import get_monitor, get_prometheus_metrics

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynOS Metrics Server",
    description="Performance monitoring and metrics collection for SynOS",
    version="1.0.0"
)

# Global monitor instance
monitor = get_monitor()

@app.on_event("startup")
async def startup_event():
    """Start the performance monitoring when server starts"""
    logger.info("Starting SynOS Metrics Server")
    asyncio.create_task(monitor.start_monitoring())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring when server shuts down"""
    logger.info("Shutting down SynOS Metrics Server")
    monitor.stop_monitoring()

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "synos-metrics"}

@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint"""
    metrics_data = get_prometheus_metrics()
    return PlainTextResponse(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

@app.get("/health/detailed")
async def detailed_health() -> Dict[str, Any]:
    """Detailed health report"""
    return monitor.get_health_report()

@app.get("/status")
async def status() -> Dict[str, Any]:
    """Current system status"""
    report = monitor.get_health_report()
    return {
        "overall_status": report.get("status", "unknown"),
        "health_score": report.get("health_score", 0),
        "monitoring_active": monitor.running,
        "snapshots_collected": len(monitor.snapshots)
    }

@app.post("/consciousness/operation")
async def record_consciousness_operation(
    operation_type: str,
    duration: float,
    success: bool = True
) -> Dict[str, str]:
    """Record a consciousness operation manually"""
    monitor.consciousness_monitor.record_operation(operation_type, duration, success)
    return {"status": "recorded"}

@app.post("/security/event")
async def record_security_event(
    event_type: str,
    severity: str
) -> Dict[str, str]:
    """Record a security event manually"""
    monitor.security_monitor.record_security_event(event_type, severity)
    return {"status": "recorded"}

@app.get("/components/consciousness")
async def consciousness_metrics() -> Dict[str, Any]:
    """Get consciousness component metrics"""
    return await monitor.consciousness_monitor.collect_metrics()

@app.get("/components/security")
async def security_metrics() -> Dict[str, Any]:
    """Get security component metrics"""
    return await monitor.security_monitor.collect_metrics()

@app.get("/components/kernel")
async def kernel_metrics() -> Dict[str, Any]:
    """Get kernel component metrics"""
    return await monitor.kernel_monitor.collect_metrics()

if __name__ == "__main__":
    uvicorn.run(
        "metrics_server:app",
        host="0.0.0.0",
        port=9090,
        log_level="info"
    )
