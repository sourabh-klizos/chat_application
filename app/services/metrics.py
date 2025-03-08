import psutil
from prometheus_client import Counter, Summary, generate_latest, Gauge, Histogram

# HTTP Metrics
HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP Requests")
HTTP_REQUEST_DURATION = Summary(
    "http_request_duration_seconds", "Duration of HTTP requests in seconds"
)

# WebSocket Metrics
WS_CONNECTIONS_ACTIVE = Gauge(
    "ws_connections_active", "Number of active WebSocket connections"
)
WS_CONNECTIONS_TOTAL = Counter("ws_connections_total", "Total WebSocket Connections")
WS_MESSAGES = Counter("ws_messages_total", "Total WebSocket Messages")

MESSAGE_PROCESSING_TIME = Histogram(
    "ws_message_processing_duration_seconds",
    "Time taken to process WebSocket messages ",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5, 1, 2],
)


# System Metrics
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")


# redis
REDIS_CHANNELS_ACTIVE = Gauge(
    "redis_channels_active", "Number of active Redis channels"
)
REDIS_CHANNELS_TOTAL = Counter("redis_channels_total", "Total Redis channels created")

# mongodb
MONGO_DB_CONNECTIONS = Counter(
    "mongodb_connections_total", "Total MongoDb Connection created"
)


# Function to update system metrics (called only when Prometheus scrapes)
def update_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)


def get_metrics():
    """
    Returns the latest Prometheus metrics after updating them.

    Updates metrics before responding to a Prometheus scrape request.
    """
    update_metrics()
    return generate_latest()
