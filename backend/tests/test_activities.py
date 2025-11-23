import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    return resp.json()["access_token"]

def test_get_activities():
    token = get_token()
    resp = client.get("/activities", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
