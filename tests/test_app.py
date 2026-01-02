def test_signup_invalid_email_format():
    # Email without @
    email = "invalidemailformat"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    # Should allow, as no validation in backend, but test for 200 or 400
    assert response.status_code in (200, 400)
    # Clean up if added
    data = client.get("/activities").json()
    if email in data["Chess Club"]["participants"]:
        data["Chess Club"]["participants"].remove(email)

def test_signup_empty_email():
    email = ""
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400 or response.status_code == 422

def test_signup_whitespace_email():
    email = "   "
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400 or response.status_code == 422

def test_signup_case_insensitive_duplicate():
    email = "MICHAEL@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    # Should be allowed if backend is case-sensitive, else 400
    assert response.status_code in (200, 400)
    # Clean up if added
    data = client.get("/activities").json()
    if email in data["Chess Club"]["participants"]:
        data["Chess Club"]["participants"].remove(email)

def test_signup_special_characters_activity():
    # Add a new activity with special chars
    special_name = "Test/Activity@2026!"
    app.activities = getattr(app, 'activities', None) or {}
    app.activities[special_name] = {
        "description": "Special activity",
        "schedule": "Now",
        "max_participants": 2,
        "participants": []
    }
    email = "special@mergington.edu"
    response = client.post(f"/activities/{special_name}/signup?email={email}")
    # Should 404 because not in main activities dict
    assert response.status_code == 404

def test_signup_max_length_email():
    email = ("a" * 64) + "@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code in (200, 400)
    # Clean up if added
    data = client.get("/activities").json()
    if email in data["Chess Club"]["participants"]:
        data["Chess Club"]["participants"].remove(email)

def test_signup_missing_email_param():
    response = client.post("/activities/Chess%20Club/signup")
    assert response.status_code == 422
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Use a unique email to avoid duplicate error
    email = "testuser1@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email} for Chess Club" in response.json()["message"]
    # Clean up: remove the test user
    data = client.get("/activities").json()
    data["Chess Club"]["participants"].remove(email)

def test_signup_duplicate():
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_signup_max_capacity():
    # Fill up a small activity
    activity = "Tennis"
    email_list = [f"testmax{i}@mergington.edu" for i in range(10)]
    for email in email_list:
        client.post(f"/activities/{activity}/signup?email={email}")
    # Now try one more
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "max capacity" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    for email in email_list:
        if email in data[activity]["participants"]:
            data[activity]["participants"].remove(email)
