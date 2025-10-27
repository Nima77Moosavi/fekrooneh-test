import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# -------------------------------------------------------------------
# Test setup/teardown
# -------------------------------------------------------------------
# Before each test, drop and recreate all tables so we start fresh.
# After each test, drop everything again to avoid data leakage.
@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# -------------------------------------------------------------------
# User creation + check-in tests
# -------------------------------------------------------------------
def test_create_user_and_checkin():
    """
    Verify that:
    - A user can be created successfully.
    - First check-in gives +10 XP and streak = 1.
    - Second check-in on the same day does not increase XP/streak.
    """
    # Create a user
    response = client.post("/users/?username=testuser")
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    # First check-in
    response = client.post(f"/checkin/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["xp"] == 10
    assert data["streak"] == 1

    # Second check-in same day → should not add XP
    response = client.post(f"/checkin/{user_id}")
    data = response.json()
    assert data["message"] == "Already checked in today"
    assert data["xp"] == 10
    assert data["streak"] == 1


def test_checkin_nonexistent_user():
    """
    Verify that checking in with an invalid user_id returns 404.
    """
    response = client.post("/checkin/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# -------------------------------------------------------------------
# League assignment tests
# -------------------------------------------------------------------
def test_league_assignment():
    """
    Verify that:
    - Users are distributed into leagues of 50.
    - League 1 contains the top 50 users by XP.
    - League 2 contains the next 10 users (since we created 60 total).
    """
    # Create 60 users
    for i in range(60):
        client.post(f"/users/?username=user{i}")

    # Give XP to first 10 users (so they rank higher)
    for i in range(1, 11):
        client.post(f"/checkin/{i}")

    # League 1 should have 50 users
    response = client.get("/leagues/1")
    assert response.status_code == 200
    league1 = response.json()
    assert len(league1) == 50

    # League 2 should have 10 users
    response = client.get("/leagues/2")
    assert response.status_code == 200
    league2 = response.json()
    assert len(league2) == 10

    # Ensure a high-XP user is in league 1
    top_user = league1[0]
    assert top_user["xp"] >= league1[-1]["xp"]


def test_user_league_endpoint():
    """
    Verify that /users/{id}/league returns the correct league and rank.

    NOTE:
    - This test assumes the app uses ROW_NUMBER() instead of RANK()
      for ranking, so that ties are broken deterministically and
      leagues always contain exactly 50 users.
    """
    # Create 55 users
    for i in range(55):
        client.post(f"/users/?username=user{i}")

    # Give XP to first 5 users
    for i in range(1, 6):
        client.post(f"/checkin/{i}")

    # User 1 should be in league 1 with a high rank
    response = client.get("/users/1/league")
    assert response.status_code == 200
    data = response.json()
    assert data["league_id"] == 1
    assert data["rank"] <= 5

    # User 55 should be in league 2 (since 50 per league)
    response = client.get("/users/55/league")
    assert response.status_code == 200
    data = response.json()
    assert data["league_id"] == 2


def test_user_league_nonexistent_user():
    """
    Verify that requesting league info for a non-existent user returns 404.
    """
    response = client.get("/users/999/league")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
