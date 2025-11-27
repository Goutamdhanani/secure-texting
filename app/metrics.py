# Lightweight Prometheus metrics helper (no import of app to avoid circular imports)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi import Response
import time

# Counters & histograms
MESSAGES_SENT = Counter(
    "app_messages_sent_total",
    "Total number of encrypted messages sent",
)

REQUESTS_TOTAL = Counter(
    "app_http_requests_total",
    "Total HTTP requests processed",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY_SECONDS = Histogram(
    "app_request_latency_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)

def metrics_response() -> Response:
    """
    Return a Starlette/FastAPI Response containing Prometheus metrics.
    Uses the global REGISTRY (single-process uvicorn). For multiprocess setups,
    additional configuration is required.
    """
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

def observe_request(endpoint: str, method: str, status: int, elapsed: float):
    try:
        REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
        REQUEST_LATENCY_SECONDS.labels(endpoint=endpoint).observe(elapsed)
    except Exception:
        # Never raise from metrics collection
        pass
