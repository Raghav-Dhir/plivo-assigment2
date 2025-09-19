import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, Deque

logger = logging.getLogger("pubsub")

REPLAY_BUFFER_SIZE = int(__import__("os").environ.get("REPLAY_SIZE", 100))
SUBSCRIBER_QUEUE_SIZE = int(__import__("os").environ.get("QUEUE_SIZE", 100))

@dataclass
class Subscriber:
    client_id: str
    websocket: any
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=SUBSCRIBER_QUEUE_SIZE))
    closed: bool = False

@dataclass
class Topic:
    name: str
    subscribers: Dict[str, Subscriber] = field(default_factory=dict)
    replay_buffer: Deque[Dict[str, Any]] = field(default_factory=lambda: deque(maxlen=REPLAY_BUFFER_SIZE))
    total_messages: int = 0

class TopicManager:
    def __init__(self):
        self._topics: Dict[str, Topic] = {}
        self._lock = asyncio.Lock()

    async def create_topic(self, name: str) -> Topic:
        async with self._lock:
            if name in self._topics:
                raise ValueError("topic_exists")
            t = Topic(name=name)
            self._topics[name] = t
            logger.info("Created topic %s", name)
            return t

    async def delete_topic(self, name: str):
        async with self._lock:
            if name not in self._topics:
                raise KeyError("not_found")
            t = self._topics.pop(name)
        # notify subscribers
        for sub in list(t.subscribers.values()):
            try:
                await sub.queue.put_nowait({"type": "info", "info": "topic_deleted", "topic": name})
            except Exception:
                pass
            try:
                await sub.websocket.close(code=1001)
            except Exception:
                pass

    async def get_topic(self, name: str) -> Topic:
        async with self._lock:
            t = self._topics.get(name)
            if not t:
                raise KeyError("not_found")
            return t

    async def list_topics(self):
        async with self._lock:
            return list(self._topics.values())

topic_manager = TopicManager()
