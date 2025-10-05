"""Security tests for RBAC, IDOR, and SQL injection."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Site, Tenant, User


@pytest.mark.security
def test_sql_injection_in_email(client: TestClient) -> None:
    """Test SQL injection protection in email field."""
    # Try SQL injection in magic link request
    response = client.post(
        "/v1/auth/magic-link",
        json={"email": "admin' OR '1'='1"},
    )

    # Should fail validation (invalid email format)
    assert response.status_code == 422


@pytest.mark.security
def test_tenant_isolation(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that tenants are properly isolated."""
    # Create two tenants
    tenant1 = Tenant(name="Tenant 1", created_at=datetime.utcnow())
    tenant2 = Tenant(name="Tenant 2", created_at=datetime.utcnow())
    db.add_all([tenant1, tenant2])
    db.flush()

    # Create sites for each tenant
    site1 = Site(
        tenant_id=tenant1.id,
        url="https://tenant1.com",
        created_at=datetime.utcnow(),
    )
    site2 = Site(
        tenant_id=tenant2.id,
        url="https://tenant2.com",
        created_at=datetime.utcnow(),
    )
    db.add_all([site1, site2])
    db.commit()

    # Admin user is associated with tenant1
    # Try to access tenant2's site
    response = client.get(
        f"/v1/sites/{site2.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.security
def test_member_cannot_create_sites(
    client: TestClient,
    member_auth_headers: dict[str, str],
) -> None:
    """Test that member role cannot create sites."""
    response = client.post(
        "/v1/sites",
        json={"url": "https://example.com"},
        headers=member_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.security
def test_member_cannot_trigger_runs(
    client: TestClient,
    db: Session,
    test_tenant,
    member_auth_headers: dict[str, str],
) -> None:
    """Test that member role cannot trigger runs."""
    site = Site(
        tenant_id=test_tenant.id,
        url="https://example.com",
        created_at=datetime.utcnow(),
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    response = client.post(
        f"/v1/sites/{site.id}/run",
        headers=member_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.security
def test_unauthenticated_access_denied(client: TestClient) -> None:
    """Test that unauthenticated requests are denied."""
    endpoints = [
        "/v1/auth/me",
        "/v1/tenants",
        "/v1/sites",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


@pytest.mark.security
def test_idor_attempt_with_uuid(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test IDOR protection with UUID."""
    # Create another tenant
    other_tenant = Tenant(name="Other Tenant", created_at=datetime.utcnow())
    db.add(other_tenant)
    db.flush()

    # Create site for other tenant
    other_site = Site(
        tenant_id=other_tenant.id,
        url="https://other.com",
        created_at=datetime.utcnow(),
    )
    db.add(other_site)
    db.commit()

    # Try to trigger run on other tenant's site
    response = client.post(
        f"/v1/sites/{other_site.id}/run",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403

