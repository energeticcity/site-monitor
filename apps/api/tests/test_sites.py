"""Tests for sites endpoints."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session

from app.models import Site, User
from app.services.worker_client import WorkerResponse


@pytest.mark.integration
def test_create_site(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test creating a site."""
    response = client.post(
        "/v1/sites",
        json={
            "url": "https://example.com",
            "profile_key": None,
            "interval_minutes": 60,
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["enabled"] is True

    # Verify in database
    site = db.query(Site).filter(Site.url == "https://example.com").first()
    assert site is not None


@pytest.mark.security
def test_create_site_as_member_forbidden(
    client: TestClient,
    member_user: User,
    member_auth_headers: dict[str, str],
) -> None:
    """Test that member cannot create sites."""
    response = client.post(
        "/v1/sites",
        json={"url": "https://example.com"},
        headers=member_auth_headers,
    )

    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]


@pytest.mark.integration
def test_list_sites(
    client: TestClient,
    db: Session,
    admin_user: User,
    test_tenant,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test listing sites."""
    # Create a site
    site = Site(
        tenant_id=test_tenant.id,
        url="https://example.com",
        created_at=datetime.utcnow(),
    )
    db.add(site)
    db.commit()

    response = client.get("/v1/sites", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["sites"]) >= 1


@pytest.mark.integration
@respx.mock
def test_trigger_run_with_discover(
    client: TestClient,
    db: Session,
    admin_user: User,
    test_tenant,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test triggering a run with discover method."""
    # Create a site
    site = Site(
        tenant_id=test_tenant.id,
        url="https://example.com",
        created_at=datetime.utcnow(),
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    # Mock Worker response
    respx.post("https://your-worker.workers.dev/discover").mock(
        return_value=Response(
            200,
            json={
                "source": "html",
                "links": [
                    "https://example.com/post1",
                    "https://example.com/post2",
                ],
                "count": 2,
            },
        )
    )

    response = client.post(
        f"/v1/sites/{site.id}/run",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "run_id" in data


@pytest.mark.integration
@respx.mock
def test_trigger_run_with_rcmp_profile(
    client: TestClient,
    db: Session,
    admin_user: User,
    test_tenant,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test triggering a run with RCMP FSJ profile."""
    # Create a site with profile
    site = Site(
        tenant_id=test_tenant.id,
        url="https://example.com",
        profile_key="rcmp_fsj",
        created_at=datetime.utcnow(),
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    # Mock Worker response
    respx.post("https://your-worker.workers.dev/profiles/rcmp-fsj").mock(
        return_value=Response(
            200,
            json={
                "source": "rcmp_fsj",
                "links": [
                    "https://bc-cb.rcmp-grc.gc.ca/post1",
                ],
                "count": 1,
            },
        )
    )

    response = client.post(
        f"/v1/sites/{site.id}/run",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.security
def test_trigger_run_as_member_forbidden(
    client: TestClient,
    db: Session,
    test_tenant,
    member_user: User,
    member_auth_headers: dict[str, str],
) -> None:
    """Test that member cannot trigger runs."""
    # Create a site
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
def test_access_other_tenant_site_forbidden(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test IDOR: cannot access other tenant's site."""
    # Create another tenant and site
    from app.models import Tenant

    other_tenant = Tenant(name="Other Tenant", created_at=datetime.utcnow())
    db.add(other_tenant)
    db.flush()

    other_site = Site(
        tenant_id=other_tenant.id,
        url="https://other.com",
        created_at=datetime.utcnow(),
    )
    db.add(other_site)
    db.commit()
    db.refresh(other_site)

    # Try to access other tenant's site
    response = client.get(
        f"/v1/sites/{other_site.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403
    assert "Access to this tenant not allowed" in response.json()["detail"]

