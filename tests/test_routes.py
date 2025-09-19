import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture
def topic_name():
    return "orders"

def test_create_topic(topic_name):
    r = client.post("/topics", json={"name": topic_name})
    assert r.status_code == 200
    assert r.json()["name"] == topic_name

def test_create_topic_no_name():
    r = client.post("/topics", json={})
    assert r.status_code == 400
    assert r.json()["detail"] == "name required"

def test_create_existing_topic(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.post("/topics", json={"name": topic_name})
    assert r.status_code == 409
    assert r.json()["error"] == "topic_exists"

def test_delete_topic(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.delete(f"/topics/{topic_name}")
    assert r.status_code == 200
    assert r.json()["deleted"] == topic_name

def test_delete_nonexistent_topic():
    r = client.delete("/topics/unknown")
    assert r.status_code == 404
    assert r.json()["detail"] == "topic_not_found"

def test_list_topics(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.get("/topics")
    assert r.status_code == 200
    assert any(t["name"] == topic_name for t in r.json())

def test_health_endpoint(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["topics"] >= 1

def test_stats_endpoint(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.get("/stats")
    assert r.status_code == 200
    stats = r.json()
    assert any(t["name"] == topic_name for t in stats["topics"])

def test_metrics_endpoint(topic_name):
    client.post("/topics", json={"name": topic_name})
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
