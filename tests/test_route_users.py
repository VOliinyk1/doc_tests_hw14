from unittest.mock import MagicMock
from src.database.models import User


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.users.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.users.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed_email(client, user, monkeypatch):
    response = client.post("api/auth/login",
                           data={"username": user.get("email"),
                                 "password": user.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == "Email not confirmed"


def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['token_type'] == "bearer"


def test_login_user_wrong_password(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    response = client.post("/api/auth/login",
                           data={"username": user.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_user_wrong_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    response = client.post("/api/auth/login",
                           data={"username": "some_email@test.com", "password": user.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"
