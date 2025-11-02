import pytest

def test_create_user_success(client):
    # Create a new user
    response = client.post(
        "/users/",
        params={"username": "john", "password": "pw"}
    )
    assert response.status_code == 200
    data = response.json()

    # Verify returned fields
    assert data["username"] == "john"
    assert data["xp"] == 0
    assert data["streak"] == 0
    assert data["max_streak"] == 0
    assert data["frozen_days"] == 0 or data["frozen_days"] == 1  # depending on your business rule
    assert data["rank"] is not None
    assert data["league_id"] is not None


def test_create_user_duplicate_username(client):
    # Create a user
    client.post("/users/", params={"username": "jane", "password": "pw"})

    # Try creating the same username again
    response = client.post("/users/", params={"username": "jane", "password": "pw"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_get_user_success(client):
    # Create a user
    client.post("/users/", params={"username": "alice", "password": "pw"})

    # Retrieve the user
    response = client.get("/users/alice")
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "alice"
    assert data["xp"] == 0
    assert data["streak"] == 0
    assert data["max_streak"] == 0
    assert data["frozen_days"] == 0 or data["frozen_days"] == 1


def test_get_user_not_found(client):
    response = client.get("/users/ghost")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
