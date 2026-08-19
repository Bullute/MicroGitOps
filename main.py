import time
import math
import asyncio

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="MicroGitOps Core App")

# Define Prometheus metrics for observability
REQUEST_COUNT = Counter(
    "microgitops_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "microgitops_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

@app.middleware("http")
async def monitor_requests(request, call_next):
    """Middleware to measure HTTP request latency and count requests."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Exclude metrics/health scraping itself from application stats to avoid noise
    if request.url.path not in ["/metrics", "/health"]:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            http_status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

    return response

@app.get("/")
async def read_root():
    return {"message": "Welcome to MicroGitOps Core Service!"}

@app.get("/health")
async def health_check():
    """Liveness and Readiness Probe Endpoint - Non-blocking async response."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus scraping."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def _do_burn(duration: int) -> int:
    """Synchronous CPU burn function executed in worker thread pool."""
    start = time.time()
    count = 0
    while time.time() - start < duration:
        n = 100_000 + (count % 1000)
        all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))
        count += 1
    return count

@app.get("/burn")
async def cpu_burn(duration: int = 5):
    """
    HPA Test Endpoint: Intentional CPU burn for auto-scaling demos.
    Offloaded to worker thread pool via asyncio.to_thread so main event loop never blocks.
    """
    duration = min(duration, 30)  # Safety cap
    start = time.time()
    count = await asyncio.to_thread(_do_burn, duration)
    elapsed = time.time() - start
    return {
        "status": "burn complete",
        "duration_seconds": round(elapsed, 2),
        "computations": count,
        "message": "CPU was intentionally stressed for HPA scaling demo"
    }
