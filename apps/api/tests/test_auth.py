"""Tests for auth endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.routers.auth import magic_links


@pytest.mark.unit
def test_request_magic_link(client: TestClient) -> None:
    """Test magic link request."""
    response = client.post(
        "/v1/auth/magic-link",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Magic link sent" in data["message"]


@pytest.mark.unit
def test_magic_link_callback_creates_user(client: TestClient, db: Session) -> None:
    """Test magic link callback creates new user."""
    # Request magic link first
    response = client.post(
        "/v1/auth/magic-link",
        json={"email": "newuser@example.com"},
    )
    assert response.status_code == 200

    # Get token from magic_links dict
    token = list(magic_links.keys())[0]

    # Callback with token
    response = client.post(
        "/v1/auth/magic-link/callback",
        json={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"

    # Verify user was created
    user = db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None


@pytest.mark.unit
def test_magic_link_callback_existing_user(
    client: TestClient, db: Session, super_admin_user: User
) -> None:
    """Test magic link callback with existing user."""
    # Request magic link
    response = client.post(
        "/v1/auth/magic-link",
        json={"email": super_admin_user.email},
    )
    assert response.status_code == 200

    # Get token
    token = list(magic_links.keys())[0]

    # Callback
    response = client.post(
        "/v1/auth/magic-link/callback",
        json={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == super_admin_user.email
    assert str(data["user"]["id"]) == str(super_admin_user.id)


@pytest.mark.unit
def test_magic_link_callback_invalid_token(client: TestClient) -> None:
    """Test magic link callback with invalid token."""
    response = client.post(
        "/v1/auth/magic-link/callback",
        json={"token": "invalid-token"},
    )

    assert response.status_code == 400
    assert "Invalid or expired token" in response.json()["detail"]


@pytest.mark.unit
def test_get_me(client: TestClient, super_admin_with_tenant: User, auth_headers: dict[str, str]) -> None:
    """Test get current user."""
    response = client.get("/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == super_admin_with_tenant.email
    assert len(data["tenants"]) > 0


@pytest.mark.unit
def test_get_me_unauthenticated(client: TestClient) -> None:
    """Test get current user without authentication."""
    response = client.get("/v1/auth/me")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

