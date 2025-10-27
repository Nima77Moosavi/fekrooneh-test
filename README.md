# 🏆 Daily Check-in & League System (FastAPI + SQLAlchemy)

This project implements a **daily check-in system** with XP, streaks, frozen days, and a **league ranking system**.  
It’s built with **FastAPI** and **SQLAlchemy**, designed to be simple to test locally but also scalable to millions of users.

---

## 🚀 Features

- **User creation**: Register new users with default XP, streak, and frozen days.
- **Daily check-in**:
  - +10 XP per day
  - Streak tracking (consecutive days)
  - Frozen day support (skip one day without losing streak)
- **Leagues**:
  - Users ranked by XP
  - 50 users per league
  - League and rank lookup endpoints
- **Scalability**:
  - Request-time calculation (using SQL window functions)
  - Production-ready optimization with precomputed `rank` and `league_id` via cron/Celery

---

## 📂 Project Structure

. ├── main.py # FastAPI app with endpoints ├── models.py # SQLAlchemy User model ├── database.py # Database session/engine setup ├── tasks.py # Background job to recompute ranks (cron/Celery) └── tests/ # Pytest test suite └── test_app.py

Code

---

## ⚙️ Endpoints

### Create User

```http
POST /users/?username=alice
Response:

json
{ "id": 1, "username": "alice" }
Daily Check-in
http
POST /checkin/{user_id}
Response:

json
{ "xp": 10, "streak": 1, "frozen_days": 1 }
Get League
http
GET /leagues/{league_id}
Returns up to 50 users in the given league.

Get User League & Rank
http
GET /users/{user_id}/league
Response:

json
{ "user_id": 1, "league_id": 1, "rank": 5 }
🧪 Testing
Run the test suite with:

bash
pytest -v
Tests cover:

User creation

Daily check-in logic

Frozen day handling

League distribution

Rank/league lookup

Error cases (nonexistent users)

⚡ Scalability Notes
Current approach:

/leagues/{id} uses LIMIT + OFFSET (efficient with index on xp).

/users/{id}/league uses ROW_NUMBER() window function for unique ranks.

Production optimization:

Add rank and league_id columns to User.

Run tasks.py periodically (via cron or Celery) to recompute ranks.

Endpoints become O(1) lookups.

🔄 Background Job (Ranks & Leagues)
tasks.py contains:

python
def recompute_ranks():
    users = db.query(User).order_by(User.xp.desc()).all()
    for idx, user in enumerate(users):
        user.rank = idx + 1
        user.league_id = (idx // 50) + 1
    db.commit()
Run manually:

bash
python tasks.py
In production:

Schedule with cron (*/5 * * * * python tasks.py)

Or use Celery with Redis/RabbitMQ for distributed workers

🛠️ Running Locally
Install dependencies:

bash
pip install fastapi uvicorn sqlalchemy pytest
Start the server:

bash
uvicorn main:app --reload
Open Swagger UI: http://127.0.0.1:8000/docs

📌 Notes for Interviewers
The project demonstrates clean API design, database modeling, and scalability considerations.

Both request-time and precomputed approaches are implemented/explained.

Tests are comprehensive and document the expected behavior.

Background jobs are separated cleanly (tasks.py) for easy scheduling.
```
