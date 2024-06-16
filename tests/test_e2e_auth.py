from unittest.mock import Mock, patch, AsyncMock
from faker import Faker

from conftest import get_token

import pytest

from src.database.models import User
from src.services.auth import auth_service
from src.routes import auth

fake = Faker()
user_data = {"username": "testliza", "email": fake.email(), "password": "12345678"}
existed_user = {"username": "deadpool", "email": "deadpool@example.com", "password": "12345678"}


def test_register(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_register_account_exists(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=existed_user)
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Account already exists"
