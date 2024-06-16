from unittest.mock import AsyncMock


def test_get_contacts(client, get_token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get("api/contacts/", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200


def test_add_contacts(client, get_token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.post("api/contacts/", headers={"Authorization": f"Bearer {get_token}"}, json={
            "name": "test",
            "surname": "test",
            "phone": "123456789",
            "email": "test@test.com",
            "birthday": "2021-01-01",
            "description": "test description"
        })
    assert response.status_code == 201


def test_get_contact(client, get_token, monkeypatch):
    contact_id = 1
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get(f"api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"},)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id
