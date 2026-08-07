import time

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
def read_root():
    return {"message": "Welcome to MicroGitOps Core Service!"}

@app.get("/health")
def health_check():
    """Liveness and Readiness Probe Endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    """Endpoint for Prometheus scraping."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
