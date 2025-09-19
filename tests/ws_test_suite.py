import pytest
from fastapi.testclient import TestClient
import json
import time
from app import app

client = TestClient(app)

@pytest.fixture
def topic_name():
    return "orders"

@pytest.fixture
def client_id():
    return "test-client"

def create_topic(topic_name):
    client.post("/topics", json={"name": topic_name})

def websocket_subscribe(ws, topic_name, client_id, request_id="req-1"):
    sub_msg = {
        "type": "subscribe",
        "topic": topic_name,
        "client_id": client_id,
        "last_n": 0,
        "request_id": request_id
    }
    ws.send_text(json.dumps(sub_msg))
    # Receive subscription ACK
    ack = ws.receive_json()
    assert ack["type"] == "ack"
    assert ack["action"] == "subscribe"
    assert ack["topic"] == topic_name
    assert ack["request_id"] == request_id

def websocket_publish(ws, topic_name, message_id, payload, request_id="req-2"):
    pub_msg = {
        "type": "publish",
        "topic": topic_name,
        "message": {"id": message_id, "payload": payload},
        "request_id": request_id
    }
    ws.send_text(json.dumps(pub_msg))
    # Receive publish ACK
    ack = ws.receive_json()
    assert ack["type"] == "ack"
    assert ack["action"] == "publish"
    assert ack["topic"] == topic_name
    assert ack["request_id"] == request_id

def websocket_receive_event(ws, timeout=0.1):
    """Poll for an event message from WebSocket"""
    start_time = time.time()
    while True:
        try:
            msg = ws.receive_json()
            if msg["type"] == "event":
                return msg
        except Exception:
            pass
        if time.time() - start_time > timeout:
            raise TimeoutError("Did not receive event message")
        time.sleep(0.01)

# -----------------------------
# Tests
# -----------------------------

def test_subscribe_nonexistent_topic(client_id):
    with client.websocket_connect("/ws") as ws:
        sub_msg = {
            "type": "subscribe",
            "topic": "nonexistent",
            "client_id": client_id,
            "last_n": 0,
            "request_id": "req-3"
        }
        ws.send_text(json.dumps(sub_msg))
        error = ws.receive_json()
        assert error["type"] == "error"
        assert error["code"] == "TOPIC_NOT_FOUND"
        ws.close()

def test_unsubscribe(topic_name, client_id):
    create_topic(topic_name)
    with client.websocket_connect("/ws") as ws:
        # Subscribe
        websocket_subscribe(ws, topic_name, client_id)

        # Unsubscribe
        unsub_msg = {
            "type": "unsubscribe",
            "topic": topic_name,
            "client_id": client_id,
            "request_id": "req-4"
        }
        ws.send_text(json.dumps(unsub_msg))
        ack = ws.receive_json()
        assert ack["type"] == "ack"
        assert ack["action"] == "unsubscribe"
        assert ack["topic"] == topic_name
        ws.close()
