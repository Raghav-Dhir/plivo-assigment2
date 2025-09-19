from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from core.topic_manager import topic_manager

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
    return {"name": name}

@router.delete("/topics/{name}")
async def delete_topic(name: str):
    try:
        await topic_manager.delete_topic(name)
    except KeyError:
        raise HTTPException(status_code=404, detail="topic_not_found")
    return {"deleted": name}

@router.get("/topics")
async def list_topics():
    topics = await topic_manager.list_topics()
    return [{"name": t.name, "subscribers": len(t.subscribers), "messages": t.total_messages} for t in topics]

@router.get("/health")
async def health():
    topics = await topic_manager.list_topics()
    total_subs = sum(len(t.subscribers) for t in topics)
    return {"status": "ok", "topics": len(topics), "subscribers": total_subs}

@router.get("/stats")
async def stats():
    topics = await topic_manager.list_topics()
    return {"topics":[{"name":t.name,"subscribers":len(t.subscribers),"messages":t.total_messages} for t in topics]}
