"""Tests for tenants endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Tenant, User


@pytest.mark.unit
def test_create_tenant_as_super_admin(
    client: TestClient,
    db: Session,
    super_admin_with_tenant: User,
    auth_headers: dict[str, str],
) -> None:
    """Test creating tenant as super admin."""
    response = client.post(
        "/v1/tenants",
        json={"name": "New Tenant", "plan": "pro"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Tenant"
    assert data["plan"] == "pro"

    # Verify in database
    tenant = db.query(Tenant).filter(Tenant.name == "New Tenant").first()
    assert tenant is not None


@pytest.mark.security
def test_create_tenant_as_admin_forbidden(
    client: TestClient,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that non-super-admin cannot create tenant."""
    response = client.post(
        "/v1/tenants",
        json={"name": "Unauthorized Tenant", "plan": "free"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 403
    assert "Super admin access required" in response.json()["detail"]


@pytest.mark.unit
def test_list_tenants_as_super_admin(
    client: TestClient,
    super_admin_with_tenant: User,
    test_tenant: Tenant,
    auth_headers: dict[str, str],
) -> None:
    """Test listing tenants as super admin."""
    response = client.get("/v1/tenants", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["tenants"]) >= 1


@pytest.mark.security
def test_list_tenants_as_admin_forbidden(
    client: TestClient,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that non-super-admin cannot list all tenants."""
    response = client.get("/v1/tenants", headers=admin_auth_headers)

    assert response.status_code == 403

