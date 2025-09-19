from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

messages_published_total = Counter(
    "messages_published_total", "Total number of published messages"
)
messages_dropped_total = Counter(
    "messages_dropped_total", "Total number of messages dropped due to backpressure"
)

subscribers_connected = Gauge(
    "subscribers_connected", "Current number of connected subscribers"
)
topics_total = Gauge("topics_total", "Current number of topics")

def prometheus_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
