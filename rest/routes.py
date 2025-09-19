from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse

from core.metrics import topics_total, prometheus_metrics
from core.topic_manager import topic_manager
import time
from core.config import START_TIME

router = APIRouter()

@router.post("/topics")
async def create_topic(payload: dict):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    try:
        await topic_manager.create_topic(name)
    except ValueError:
        return JSONResponse({"error":"topic_exists"}, status_code=409)
    return {"status": "created", "topic": name}

@router.delete("/topics/{name}")
async def delete_topic(name: str):
    try:
        await topic_manager.delete_topic(name)
    except KeyError:
        raise HTTPException(status_code=404, detail="topic_not_found")
    return {"status": "deleted", "topic": name}

@router.get("/topics")
async def list_topics():
    topics = await topic_manager.list_topics()
    topics_list = [
        {"name": t.name, "subscribers": len(t.subscribers)}
        for t in topics
    ]
    return {"topics": topics_list}

@router.get("/health")
async def health():
    topics = await topic_manager.list_topics()
    total_subs = sum(len(t.subscribers) for t in topics)
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "topics": len(topics),
        "subscribers": total_subs,
        "uptime_seconds": uptime_seconds
    }

@router.get("/stats")
async def stats():
    topics = await topic_manager.list_topics()
    topics_dict = {
        t.name: {
            "messages": t.total_messages,
            "subscribers": len(t.subscribers)
        } for t in topics
    }
    return {"topics": topics_dict}

@router.get("/metrics")
async def metrics():
    topics = await topic_manager.list_topics()
    topics_total.set(len(topics))
    data, content_type = prometheus_metrics()
    return Response(content=data, media_type=content_type)
