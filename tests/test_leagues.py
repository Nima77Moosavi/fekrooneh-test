import pytest


def test_league_assignment_and_ranking(client):
    # Create 60 users with increasing XP
    for i in range(60):
        client.post(
            "/users/",
            params={"username": f"user{i}", "password": "pw", "xp": i * 10}
        )

    # Get league 1 (should contain top 50 users)
    response = client.get("/leagues/1")
    assert response.status_code == 200
    league1 = response.json()
    assert len(league1) == 50

    # Highest XP user should be rank 1
    assert league1[0]["rank"] == 1
    # Lowest XP in league 1 should be rank 50
    assert league1[-1]["rank"] == 50

    # Get league 2 (should contain remaining 10 users)
    response = client.get("/leagues/2")
    assert response.status_code == 200
    league2 = response.json()
    assert len(league2) == 10
    assert league2[0]["rank"] == 51
    assert league2[-1]["rank"] == 60


def test_get_user_league(client):
    # Create 3 users with different XP
    client.post(
        "/users/", params={"username": "alice", "password": "pw", "xp": 300})
    client.post(
        "/users/", params={"username": "bob", "password": "pw", "xp": 200})
    client.post(
        "/users/", params={"username": "charlie", "password": "pw", "xp": 100})

    # Alice should be rank 1
    resp = client.get("/users/alice/league")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"
    assert data["rank"] == 1
    assert data["league_id"] == 1

    # Charlie should be rank 3
    resp = client.get("/users/charlie/league")
    data = resp.json()
    assert data["rank"] == 3
    assert data["league_id"] == 1


def test_get_all_users_ranked(client):
    # Create 5 users with different XP values
    client.post(
        "/users/", params={"username": "u1", "password": "pw", "xp": 50})
    client.post(
        "/users/", params={"username": "u2", "password": "pw", "xp": 200})
    client.post(
        "/users/", params={"username": "u3", "password": "pw", "xp": 150})
    client.post(
        "/users/", params={"username": "u4", "password": "pw", "xp": 300})
    client.post(
        "/users/", params={"username": "u5", "password": "pw", "xp": 100})

    # Call the global ranking endpoint
    response = client.get("/league/")
    assert response.status_code == 200
    users = response.json()

    # Verify all 5 users are returned
    assert len(users) == 5

    # Verify they are sorted by rank (highest XP first)
    usernames_in_order = [u["username"] for u in users]
    assert usernames_in_order == ["u4", "u2", "u3", "u5", "u1"]

    # Verify ranks are sequential
    ranks = [u["rank"] for u in users]
    assert ranks == [1, 2, 3, 4, 5]
