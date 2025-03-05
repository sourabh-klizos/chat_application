# import psutil
# from prometheus_client import (
#     Counter,
#     Summary,
#     generate_latest,
#     CollectorRegistry,
#     Gauge,
#     Histogram,
# )


# REGISTRY = CollectorRegistry()


# HTTP_REQUESTS = Counter(
#     "http_requests_total",
#     "Total HTTP Requests",
#     ["method", "endpoint", "status_code"],
#     registry=REGISTRY,
# )
# HTTP_REQUEST_DURATION = Summary(
#     "http_request_duration_seconds",
#     "Duration of HTTP requests in seconds",
#     registry=REGISTRY,
# )


# WS_CONNECTIONS_ACTIVE = Gauge(
#     "ws_connections_active",
#  "Number of active WebSocket connections",
#        registry=REGISTRY
# )


# WS_CONNECTIONS_TOTAL = Counter(
#     "ws_connections_total",
#  "Total WebSocket Connections",
#  registry=REGISTRY
# )


# WS_MESSAGE_LATENCY = Histogram(
#     "ws_message_latency_seconds",
#     "Latency of WebSocket messages",
#     buckets=[0.1, 0.5, 1, 2, 5, 10],
#     registry=REGISTRY,
# )


# WS_MESSAGES = Counter(
#     "ws_messages_total", "Total WebSocket Messages", registry=REGISTRY
# )


# CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage", registry=REGISTRY)
# MEMORY_USAGE = Gauge(
#     "memory_usage_percent", "Memory usage percentage", registry=REGISTRY
# )


# def get_metrics():
#     CPU_USAGE.set(psutil.cpu_percent())
#     MEMORY_USAGE.set(psutil.virtual_memory().percent)

#     return generate_latest(REGISTRY)


# import psutil
# from prometheus_client import (
#     Counter,
#     Summary,
#     generate_latest,
#     CollectorRegistry,
#     Gauge,
#     Histogram,
# )

# REGISTRY = CollectorRegistry()

# # Existing metrics
# HTTP_REQUESTS = Counter(
#     "http_requests_total",
#     "Total HTTP Requests",
#     ["method", "endpoint", "status_code"],
#     registry=REGISTRY,
# )
# HTTP_REQUEST_DURATION = Summary(
#     "http_request_duration_seconds",
#     "Duration of HTTP requests in seconds",
#     registry=REGISTRY,
# )
# WS_CONNECTIONS_ACTIVE = Gauge(
#     "ws_connections_active",
#  "Number of active WebSocket connections",
#  registry=REGISTRY
# )
# WS_CONNECTIONS_TOTAL = Counter(
#     "ws_connections_total",
#  "Total WebSocket Connections", registry=REGISTRY
# )
# WS_MESSAGE_LATENCY = Histogram(
#     "ws_message_latency_seconds",
#     "Latency of WebSocket messages",
#     buckets=[0.1, 0.5, 1, 2, 5, 10],
#     registry=REGISTRY,
# )
# WS_MESSAGES = Counter(
#     "ws_messages_total", "Total WebSocket Messages", registry=REGISTRY
# )

# # New metrics

# ## CPU Metrics
# CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage", registry=REGISTRY)
# CPU_LOAD_1M = Gauge("cpu_load_1m", "CPU load average (1 min)", registry=REGISTRY)
# CPU_LOAD_5M = Gauge("cpu_load_5m", "CPU load average (5 min)", registry=REGISTRY)
# CPU_LOAD_15M = Gauge("cpu_load_15m", "CPU load average (15 min)", registry=REGISTRY)

# ## Memory Metrics
# MEMORY_USAGE = Gauge(
#     "memory_usage_percent", "Memory usage percentage", registry=REGISTRY
# )
# MEMORY_AVAILABLE = Gauge(
#     "memory_available_bytes", "Available memory in bytes", registry=REGISTRY
# )
# SWAP_USAGE = Gauge("swap_usage_percent", "Swap usage percentage", registry=REGISTRY)

# ## Disk Metrics
# DISK_USAGE = Gauge("disk_usage_percent", "Disk usage percentage", registry=REGISTRY)
# DISK_READ_BYTES = Gauge(
#     "disk_read_bytes", "Total bytes read from disk", registry=REGISTRY
# )
# DISK_WRITE_BYTES = Gauge(
#     "disk_write_bytes", "Total bytes written to disk", registry=REGISTRY
# )

# ## Network Metrics
# NETWORK_SENT = Gauge(
#     "network_sent_bytes", "Total bytes sent over network", registry=REGISTRY
# )
# NETWORK_RECEIVED = Gauge(
#     "network_received_bytes", "Total bytes received over network", registry=REGISTRY
# )

# ## Process Metrics
# RUNNING_PROCESSES = Gauge(
#     "running_processes", "Number of running processes", registry=REGISTRY
# )


# def get_metrics():
#     """Fetch and update metrics"""
#     # CPU metrics
#     CPU_USAGE.set(psutil.cpu_percent())
#     load1, load5, load15 = psutil.getloadavg()
#     CPU_LOAD_1M.set(load1)
#     CPU_LOAD_5M.set(load5)
#     CPU_LOAD_15M.set(load15)

#     # Memory metrics
#     mem = psutil.virtual_memory()
#     MEMORY_USAGE.set(mem.percent)
#     MEMORY_AVAILABLE.set(mem.available)
#     swap = psutil.swap_memory()
#     SWAP_USAGE.set(swap.percent)

#     # Disk metrics
#     disk = psutil.disk_usage("/")
#     DISK_USAGE.set(disk.percent)

#     disk_io = psutil.disk_io_counters()
#     DISK_READ_BYTES.set(disk_io.read_bytes)
#     DISK_WRITE_BYTES.set(disk_io.write_bytes)

#     # Network metrics
#     net_io = psutil.net_io_counters()
#     NETWORK_SENT.set(net_io.bytes_sent)
#     NETWORK_RECEIVED.set(net_io.bytes_recv)

#     # Process metrics
#     RUNNING_PROCESSES.set(len(psutil.pids()))

#     return generate_latest(REGISTRY)


import psutil
from prometheus_client import (
    Counter,
    Summary,
    generate_latest,
    Gauge,
    Histogram,
)

# HTTP Metrics
HTTP_REQUESTS = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status_code"]
)
HTTP_REQUEST_DURATION = Summary(
    "http_request_duration_seconds", "Duration of HTTP requests in seconds"
)

# WebSocket Metrics
WS_CONNECTIONS_ACTIVE = Gauge(
    "ws_connections_active", "Number of active WebSocket connections"
)
WS_CONNECTIONS_TOTAL = Counter("ws_connections_total", "Total WebSocket Connections")
WS_MESSAGE_LATENCY = Histogram(
    "ws_message_latency_seconds",
    "Latency of WebSocket messages",
    buckets=[0.1, 0.5, 1, 2, 5, 10],
)
WS_MESSAGES = Counter("ws_messages_total", "Total WebSocket Messages")

# System Metrics
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")


# Function to update system metrics (called only when Prometheus scrapes)
def update_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)


# Function to expose metrics
def get_metrics():
    update_metrics()  # Update metrics only when Prometheus requests
    return generate_latest()
