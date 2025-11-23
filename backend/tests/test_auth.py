import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test signup
def test_signup():
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

# Test login
def test_login():
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
