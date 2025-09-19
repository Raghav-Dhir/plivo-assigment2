import asyncio
import json
import websockets
import uuid

WS_URL = "ws://localhost:8080/ws"
TOPIC_NAME = "test"

async def subscriber1():
    async with websockets.connect(WS_URL) as ws:
        client_id = str(uuid.uuid4())
        print(f"[Subscriber1] Connected with client_id {client_id}")

        # Subscribe without last_n
        subscribe_msg = {
            "type": "subscribe",
            "topic": TOPIC_NAME,
            "client_id": client_id,
            "last_n": 0,
            "request_id": "sub1"
        }
        await ws.send(json.dumps(subscribe_msg))
        ack = await ws.recv()
        print("[Subscriber1] Received:", ack)

        # Publish 5 messages
        for i in range(1, 6):
            msg_id = str(uuid.uuid4())
            publish_msg = {
                "type": "publish",
                "topic": TOPIC_NAME,
                "message": {"id": msg_id, "payload": f"Message {i}"},
                "request_id": f"pub{i}"
            }
            await ws.send(json.dumps(publish_msg))
            ack_pub = await ws.recv()
            print(f"[Subscriber1] Published {msg_id} | Received:", ack_pub)
            await asyncio.sleep(0.05)  # let server enqueue

        print("[Subscriber1] Done publishing. Listening for events...")
        try:
            while True:
                msg = await ws.recv()
                print("[Subscriber1] Event received:", msg)
        except websockets.ConnectionClosed:
            print("[Subscriber1] Connection closed")

async def subscriber2():
    await asyncio.sleep(0.5)

    async with websockets.connect(WS_URL) as ws:
        client_id = str(uuid.uuid4())
        print(f"[Subscriber2] Connected with client_id {client_id}")

        subscribe_msg = {
            "type": "subscribe",
            "topic": TOPIC_NAME,
            "client_id": client_id,
            "last_n": 3,
            "request_id": "sub2"
        }
        await ws.send(json.dumps(subscribe_msg))
        ack = await ws.recv()
        print("[Subscriber2] Received:", ack)

        # Receive replayed messages
        replayed = []
        for _ in range(3):
            msg = await ws.recv()
            print("[Subscriber2] Replayed message:", msg)
            replayed.append(msg)

        print("[Subscriber2] Finished receiving last_n replayed messages")

        try:
            while True:
                msg = await ws.recv()
                print("[Subscriber2] Event received:", msg)
        except websockets.ConnectionClosed:
            print("[Subscriber2] Connection closed")

async def main():
    await asyncio.gather(subscriber1(), subscriber2())

if __name__ == "__main__":
    asyncio.run(main())
