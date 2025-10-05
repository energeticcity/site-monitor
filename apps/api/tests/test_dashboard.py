"""Tests for dashboard endpoints."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Item, Run, RunStatus, Site, Tenant, User


@pytest.mark.integration
def test_get_dashboard_stats(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
    test_tenant: Tenant,
) -> None:
    """Test getting dashboard statistics."""
    # Create some test data
    # Create sites
    site1 = Site(
        tenant_id=test_tenant.id,
        url="https://example1.com",
        enabled=True,
        interval_minutes=60,
        created_at=datetime.utcnow(),
    )
    site2 = Site(
        tenant_id=test_tenant.id,
        url="https://example2.com",
        enabled=False,
        interval_minutes=60,
        created_at=datetime.utcnow(),
    )
    db.add_all([site1, site2])
    db.flush()

    # Create items
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    item1 = Item(
        site_id=site1.id,
        url="https://example1.com/post1",
        canonical_url="https://example1.com/post1",
        discovered_at=now,
        source="feed",
    )
    item2 = Item(
        site_id=site1.id,
        url="https://example1.com/post2",
        canonical_url="https://example1.com/post2",
        discovered_at=week_ago - timedelta(days=1),  # Older than a week
        source="feed",
    )
    db.add_all([item1, item2])
    db.flush()

    # Create runs
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    run1 = Run(
        site_id=site1.id,
        status=RunStatus.SUCCESS,
        method="discover",
        started_at=now,
        finished_at=now,
        pages_scanned=10,
    )
    run2 = Run(
        site_id=site1.id,
        status=RunStatus.ERROR,
        method="discover",
        started_at=now,
        finished_at=now,
        pages_scanned=0,
    )
    run3 = Run(
        site_id=site2.id,
        status=RunStatus.SUCCESS,
        method="discover",
        started_at=today_start - timedelta(days=1),  # Yesterday
        finished_at=today_start - timedelta(days=1),
        pages_scanned=5,
    )
    db.add_all([run1, run2, run3])
    db.commit()

    # Make request
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={test_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["tenant_id"] == str(test_tenant.id)
    assert data["tenant_name"] == test_tenant.name
    assert data["total_sites"] == 2
    assert data["active_sites"] == 1
    assert data["total_items"] == 2
    assert data["items_this_week"] == 1  # Only item1 is within the last week
    assert data["total_runs"] == 3
    assert data["successful_runs_today"] == 1  # Only run1
    assert data["failed_runs_today"] == 1  # Only run2


@pytest.mark.integration
def test_get_dashboard_stats_empty(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
    test_tenant: Tenant,
) -> None:
    """Test getting dashboard statistics with no data."""
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={test_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["tenant_id"] == str(test_tenant.id)
    assert data["tenant_name"] == test_tenant.name
    assert data["total_sites"] == 0
    assert data["active_sites"] == 0
    assert data["total_items"] == 0
    assert data["items_this_week"] == 0
    assert data["total_runs"] == 0
    assert data["successful_runs_today"] == 0
    assert data["failed_runs_today"] == 0


@pytest.mark.security
def test_get_dashboard_stats_unauthorized(
    client: TestClient,
    test_tenant: Tenant,
) -> None:
    """Test that unauthorized users cannot access dashboard stats."""
    response = client.get(f"/v1/dashboard/stats?tenant_id={test_tenant.id}")
    assert response.status_code == 401


@pytest.mark.security
def test_get_dashboard_stats_wrong_tenant(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that users cannot access stats for other tenants."""
    # Create another tenant
    other_tenant = Tenant(
        name="Other Tenant",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)

    # Try to access other tenant's stats
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={other_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_get_team_members(
    client: TestClient,
    db: Session,
    admin_user: User,
    member_user: User,
    admin_auth_headers: dict[str, str],
    test_tenant: Tenant,
) -> None:
    """Test getting team members."""
    response = client.get(
        f"/v1/dashboard/team?tenant_id={test_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert len(data["team_members"]) == 2
    
    # Check admin user
    admin_member = next(
        (m for m in data["team_members"] if m["email"] == "admin@test.com"),
        None,
    )
    assert admin_member is not None
    assert admin_member["role"] == "admin"
    assert admin_member["name"] == "Admin User"
    
    # Check member user
    member = next(
        (m for m in data["team_members"] if m["email"] == "member@test.com"),
        None,
    )
    assert member is not None
    assert member["role"] == "member"
    assert member["name"] == "Member User"


@pytest.mark.security
def test_get_team_members_unauthorized(
    client: TestClient,
    test_tenant: Tenant,
) -> None:
    """Test that unauthorized users cannot access team members."""
    response = client.get(f"/v1/dashboard/team?tenant_id={test_tenant.id}")
    assert response.status_code == 401


@pytest.mark.security
def test_get_team_members_wrong_tenant(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that users cannot access team members for other tenants."""
    # Create another tenant
    other_tenant = Tenant(
        name="Other Tenant",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)

    # Try to access other tenant's team
    response = client.get(
        f"/v1/dashboard/team?tenant_id={other_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_member_can_view_dashboard_stats(
    client: TestClient,
    db: Session,
    member_user: User,
    member_auth_headers: dict[str, str],
    test_tenant: Tenant,
) -> None:
    """Test that members can view dashboard stats."""
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={test_tenant.id}",
        headers=member_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == str(test_tenant.id)


@pytest.mark.integration
def test_member_can_view_team_members(
    client: TestClient,
    db: Session,
    member_user: User,
    member_auth_headers: dict[str, str],
    test_tenant: Tenant,
) -> None:
    """Test that members can view team members."""
    response = client.get(
        f"/v1/dashboard/team?tenant_id={test_tenant.id}",
        headers=member_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1  # At least the member user


@pytest.mark.security
def test_super_admin_can_access_any_tenant(
    client: TestClient,
    db: Session,
    super_admin_with_tenant: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that super admin can access any tenant's dashboard."""
    # Create another tenant that super_admin is NOT directly associated with
    other_tenant = Tenant(
        name="Other Business",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)

    # Super admin should be able to access this tenant's stats
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={other_tenant.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == str(other_tenant.id)
    assert data["tenant_name"] == "Other Business"


@pytest.mark.security
def test_super_admin_can_access_any_tenant_team(
    client: TestClient,
    db: Session,
    super_admin_with_tenant: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that super admin can access any tenant's team."""
    # Create another tenant with a user
    other_tenant = Tenant(
        name="Other Business",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(other_tenant)
    db.flush()

    other_user = User(
        email="other@test.com",
        name="Other User",
        created_at=datetime.utcnow(),
    )
    db.add(other_user)
    db.flush()

    from app.models import UserTenant, Role
    user_tenant = UserTenant(
        user_id=other_user.id,
        tenant_id=other_tenant.id,
        role=Role.ADMIN,
    )
    db.add(user_tenant)
    db.commit()

    # Super admin should be able to access this tenant's team
    response = client.get(
        f"/v1/dashboard/team?tenant_id={other_tenant.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["team_members"][0]["email"] == "other@test.com"


@pytest.mark.security
def test_regular_admin_cannot_access_other_tenant(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_auth_headers: dict[str, str],
) -> None:
    """Test that regular admin cannot access other tenant's dashboard."""
    # Create another tenant
    other_tenant = Tenant(
        name="Other Business",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)

    # Admin should NOT be able to access this tenant
    response = client.get(
        f"/v1/dashboard/stats?tenant_id={other_tenant.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"].lower()

