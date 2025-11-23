import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    return resp.json()["access_token"]

def test_follow_user():
    token = get_token()
    # Create another user to follow
    client.post("/auth/signup", json={"username": "otheruser", "email": "other@example.com", "password": "otherpass"})
    resp = client.post("/users/{}/follow".format("otheruser"), headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_block_user():
    token = get_token()
    resp = client.post("/users/{}/block".format("otheruser"), headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
