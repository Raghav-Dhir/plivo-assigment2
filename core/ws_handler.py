import json
import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect
from core.models import WSMessage
from core.topic_manager import topic_manager, Subscriber
from core.utils import safe_put_to_queue

logger = logging.getLogger("pubsub")

async def handle_writer(sub: Subscriber):
    try:
        while True:
            item = await sub.queue.get()
            if item is None or sub.closed:
                break
            await sub.websocket.send_json(item)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning("Writer error for %s: %s", sub.client_id, e)
    finally:
        try: await sub.websocket.close()
        except Exception: pass

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriber_objs = {}

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = WSMessage(**json.loads(raw))
            except Exception as e:
                await websocket.send_json({"type":"error","code":"BAD_REQUEST","message":str(e)})
                continue

            rid = msg.request_id
            if msg.type == "ping":
                await websocket.send_json({"type":"pong","request_id":rid})
                continue

            if msg.type == "subscribe":
                try:
                    topic = await topic_manager.get_topic(msg.topic)
                except KeyError:
                    await websocket.send_json({"type":"error","code":"TOPIC_NOT_FOUND","request_id":rid})
                    continue
                sub = Subscriber(client_id=msg.client_id, websocket=websocket)
                subscriber_objs[msg.topic] = sub
                topic.subscribers[msg.client_id] = sub
                # replay
                if msg.last_n:
                    for m in list(topic.replay_buffer)[-msg.last_n:]:
                        await safe_put_to_queue(sub, {"type":"event","topic":topic.name,"message":m})
                asyncio.create_task(handle_writer(sub))
                await websocket.send_json({"type":"ack","action":"subscribe","topic":msg.topic,"request_id":rid})
                continue

            if msg.type == "unsubscribe":
                try:
                    topic = await topic_manager.get_topic(msg.topic)
                    sub = topic.subscribers.pop(msg.client_id, None)
                    if sub: sub.closed = True
                    await websocket.send_json({"type":"ack","action":"unsubscribe","topic":msg.topic,"request_id":rid})
                except KeyError:
                    await websocket.send_json({"type":"error","code":"TOPIC_NOT_FOUND","request_id":rid})
                continue

            if msg.type == "publish":
                try:
                    topic = await topic_manager.get_topic(msg.topic)
                except KeyError:
                    await websocket.send_json({"type":"error","code":"TOPIC_NOT_FOUND","request_id":rid})
                    continue
                m = {"id": msg.message.id, "payload": msg.message.payload}
                topic.replay_buffer.append(m)
                topic.total_messages += 1
                for sub in list(topic.subscribers.values()):
                    await safe_put_to_queue(sub, {"type":"event","topic":topic.name,"message":m})
                await websocket.send_json({"type":"ack","action":"publish","topic":msg.topic,"request_id":rid})
                continue

            await websocket.send_json({"type":"error","code":"BAD_REQUEST","message":"unknown type","request_id":rid})

    except WebSocketDisconnect:
        logger.info("Websocket disconnected")
