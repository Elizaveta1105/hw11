from unittest.mock import Mock, patch, AsyncMock

import pytest

from src.services.auth import auth_service
from src.routes import auth


def test_get_contacts(client, get_token, monkeypatch):
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.get("api/contacts/", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == []
