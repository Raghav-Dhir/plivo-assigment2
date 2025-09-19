from fastapi.testclient import TestClient
import pytest


from app import app

client = TestClient(app)

def test_create_and_list_topics():
    r = client.post("/topics", json={"name": "orders"})
    assert r.status_code == 200
    r2 = client.get("/topics")
    assert any(t["name"]=="orders" for t in r2.json())
