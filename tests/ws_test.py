import asyncio
import json
import websockets

# WebSocket URL
WS_URL = "ws://localhost:8080/ws"

async def test_websocket():
    async with websockets.connect(WS_URL) as ws:
        print("Connected to WebSocket")

        # Subscribe to topic "test"
        subscribe_msg = {"type": "subscribe", "topic": "test"}
        await ws.send(json.dumps(subscribe_msg))
        print("Subscribed to topic 'test'")

        # Publish a message to the topic
        publish_msg = {
            "type": "publish",
            "topic": "test",
            "message": {
                "id": "3f1e2b7a-8c4d-4f6a-9a12-5d2b7f1e8c9a",
                "payload": "Hello, World!"
            },
            "request_id": "req-1"
        }
        await ws.send(json.dumps(publish_msg))
        print("Published message to topic 'test'")

        # Receive messages from server
        while True:
            try:
                msg = await ws.recv()
                print("Received:", msg)
            except websockets.ConnectionClosed:
                print("Connection closed")
                break

asyncio.run(test_websocket())
