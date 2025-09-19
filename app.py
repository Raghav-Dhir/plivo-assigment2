from fastapi import FastAPI
import uvicorn
import logging
import os

from rest.routes import router as rest_router
from core.ws_handler import websocket_endpoint
from core.topic_manager import topic_manager

# Config
PORT = int(os.environ.get("PORT", 8080))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Logging
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("pubsub")

app = FastAPI()

# Mount REST routes
app.include_router(rest_router)

# Mount WebSocket route
app.add_api_websocket_route("/ws", websocket_endpoint)

@app.on_event("shutdown")
async def shutdown():
    logger.info("Graceful shutdown: notifying subscribers")
    topics = await topic_manager.list_topics()
    for t in topics:
        for sub in list(t.subscribers.values()):
            try:
                await sub.queue.put_nowait({"type":"info", "info":"server_shutdown"})
            except Exception:
                pass

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, log_level=LOG_LEVEL.lower())
