
import psutil
from prometheus_client import (
    Counter,
    Summary,
    generate_latest,
    Gauge,
)

# HTTP Metrics
HTTP_REQUESTS = Counter(
    "http_requests_total", "Total HTTP Requests"
)
HTTP_REQUEST_DURATION = Summary(
    "http_request_duration_seconds", "Duration of HTTP requests in seconds"
)

# WebSocket Metrics
WS_CONNECTIONS_ACTIVE = Gauge(
    "ws_connections_active", "Number of active WebSocket connections"
)
WS_CONNECTIONS_TOTAL = Counter("ws_connections_total", "Total WebSocket Connections")
WS_MESSAGES = Counter("ws_messages_total", "Total WebSocket Messages")

# System Metrics
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")

REDIS_CHANNELS_ACTIVE = Gauge(
    "redis_channels_active", "Number of active Redis channels"
)
REDIS_CHANNELS_TOTAL = Counter(
    "redis_channels_total", "Total Redis channels created"
)


# Function to update system metrics (called only when Prometheus scrapes)
def update_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)


# Function to expose metrics
def get_metrics():
    update_metrics()  # Update metrics only when Prometheus requests
    return generate_latest()
