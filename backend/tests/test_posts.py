import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    return resp.json()["access_token"]

def test_create_post():
    token = get_token()
    response = client.post("/posts", json={"content": "Hello World"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "Hello World"

def test_list_posts():
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
