import psutil
from prometheus_client import (
    Counter,
    Summary,
    generate_latest,
    CollectorRegistry,
    Gauge,
    Histogram,
)


REGISTRY = CollectorRegistry()


HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)
HTTP_REQUEST_DURATION = Summary(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    registry=REGISTRY,
)


WS_CONNECTIONS_ACTIVE = Gauge(
    "ws_connections_active", "Number of active WebSocket connections", registry=REGISTRY
)


WS_CONNECTIONS_TOTAL = Counter(
    "ws_connections_total", "Total WebSocket Connections", registry=REGISTRY
)


WS_MESSAGE_LATENCY = Histogram(
    "ws_message_latency_seconds",
    "Latency of WebSocket messages",
    buckets=[0.1, 0.5, 1, 2, 5, 10],
    registry=REGISTRY,
)


WS_MESSAGES = Counter(
    "ws_messages_total", "Total WebSocket Messages", registry=REGISTRY
)


CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage", registry=REGISTRY)
MEMORY_USAGE = Gauge(
    "memory_usage_percent", "Memory usage percentage", registry=REGISTRY
)


def get_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)

    return generate_latest(REGISTRY)
