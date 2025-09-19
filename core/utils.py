import logging
import asyncio
import os
from core.metrics import messages_dropped_total

logger = logging.getLogger("pubsub")

BACKPRESSURE_POLICY = os.environ.get("BACKPRESSURE", "drop_oldest")

async def safe_put_to_queue(sub, item) -> bool:
    """Put item into subscriber queue with backpressure handling"""
    try:
        sub.queue.put_nowait(item)
        return True
    except asyncio.QueueFull:
        if BACKPRESSURE_POLICY == "drop_oldest":
            try:
                _ = sub.queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                sub.queue.put_nowait(item)
                messages_dropped_total.inc()
                return True
            except asyncio.QueueFull:
                messages_dropped_total.inc()
                return False
        else:  # disconnect
            messages_dropped_total.inc()
            logger.warning("Disconnecting slow consumer %s", sub.client_id)
            try:
                await sub.websocket.send_json({
                    "type":"error", "code":"SLOW_CONSUMER",
                    "message":"disconnected due to slow consumer"
                })
                await sub.websocket.close(code=1011)
            except Exception:
                pass
            sub.closed = True
            return False
