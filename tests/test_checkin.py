import pytest
from freezegun import freeze_time
from datetime import date

def test_checkin_first_time(client):
    client.post("/users/", params={"username": "first", "password": "pw"})

    with freeze_time("2025-01-01"):
        response = client.post("/checkin/", params={"username": "first", "password": "pw"})
        data = response.json()
        assert response.status_code == 200
        assert data["streak"] == 1
        assert data["xp"] == 10
        assert data["max_streak"] == 1
        assert data["frozen_days"] == 1

def test_checkin_streak_increment(client):
    client.post("/users/", params={"username": "nima", "password": "pw"})

    with freeze_time("2025-01-01"):
        client.post("/checkin/", params={"username": "nima", "password": "pw"})

    with freeze_time("2025-01-02"):
        response = client.post("/checkin/", params={"username": "nima", "password": "pw"})
        data = response.json()
        assert data["streak"] == 2
        assert data["xp"] == 20  # deterministic now
        assert data["max_streak"] == 2


def test_checkin_twice_same_day(client):
    client.post("/users/", params={"username": "bob", "password": "pw"})

    with freeze_time("2025-01-01"):
        client.post("/checkin/", params={"username": "bob", "password": "pw"})
        response = client.post("/checkin/", params={"username": "bob", "password": "pw"})
        data = response.json()
        assert data["message"] == "Already checked in today"

def test_checkin_missed_one_day_with_freeze(client):
    client.post("/users/", params={"username": "zahra", "password": "pw"})

    with freeze_time("2025-01-01"):
        client.post("/checkin/", params={"username": "zahra", "password": "pw"})

    # Skip Jan 2, check-in on Jan 3 → streak reset, frozen day granted
    with freeze_time("2025-01-03"):
        response = client.post("/checkin/", params={"username": "zahra", "password": "pw"})
        data = response.json()
        assert data["streak"] == 1
        assert data["frozen_days"] == 0

    # Next: use frozen day
    with freeze_time("2025-01-04"):
        client.post("/checkin/", params={"username": "zahra", "password": "pw"})
    with freeze_time("2025-01-06"):  # skip Jan 5
        response2 = client.post("/checkin/", params={"username": "zahra", "password": "pw"})
        data2 = response2.json()
        assert data2["streak"] == 1  # preserved
        assert data2["frozen_days"] == 1  # consumed


def test_checkin_missed_two_days_resets(client):
    client.post("/users/", params={"username": "dave", "password": "pw"})

    with freeze_time("2025-01-01"):
        client.post("/checkin/", params={"username": "dave", "password": "pw"})

    # Skip Jan 2 and Jan 3, check-in on Jan 4 → reset
    with freeze_time("2025-01-04"):
        response = client.post("/checkin/", params={"username": "dave", "password": "pw"})
        data = response.json()
        assert data["streak"] == 1
        assert data["frozen_days"] == 1
        assert data["last_streak_reset"] == str(date(2025, 1, 4))
