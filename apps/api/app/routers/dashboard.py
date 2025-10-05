"""Dashboard router."""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_tenant_access
from app.models import Item, Run, RunStatus, Site, Tenant, User, UserTenant
from app.schemas import (
    DashboardStatsResponse,
    ItemListResponse,
    ItemResponse,
    RunListResponse,
    RunResponse,
    TeamListResponse,
    TeamMemberResponse,
)

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardStatsResponse:
    """Get dashboard statistics for a tenant."""
    # Verify user has access to this tenant
    user, role = require_tenant_access(tenant_id, current_user, db)

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Calculate statistics
    # Total sites
    total_sites = db.query(Site).filter(Site.tenant_id == tenant_id).count()

    # Active sites (enabled)
    active_sites = (
        db.query(Site)
        .filter(Site.tenant_id == tenant_id, Site.enabled == True)
        .count()
    )

    # Total items across all sites
    total_items = (
        db.query(Item)
        .join(Site)
        .filter(Site.tenant_id == tenant_id)
        .count()
    )

    # Items discovered in the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    items_this_week = (
        db.query(Item)
        .join(Site)
        .filter(
            Site.tenant_id == tenant_id,
            Item.discovered_at >= week_ago,
        )
        .count()
    )

    # Total runs
    total_runs = (
        db.query(Run)
        .join(Site)
        .filter(Site.tenant_id == tenant_id)
        .count()
    )

    # Successful runs today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    successful_runs_today = (
        db.query(Run)
        .join(Site)
        .filter(
            Site.tenant_id == tenant_id,
            Run.status == RunStatus.SUCCESS,
            Run.started_at >= today_start,
        )
        .count()
    )

    # Failed runs today
    failed_runs_today = (
        db.query(Run)
        .join(Site)
        .filter(
            Site.tenant_id == tenant_id,
            Run.status == RunStatus.ERROR,
            Run.started_at >= today_start,
        )
        .count()
    )

    return DashboardStatsResponse(
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        total_sites=total_sites,
        active_sites=active_sites,
        total_items=total_items,
        items_this_week=items_this_week,
        total_runs=total_runs,
        successful_runs_today=successful_runs_today,
        failed_runs_today=failed_runs_today,
    )


@router.get("/team", response_model=TeamListResponse)
def get_team_members(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeamListResponse:
    """Get team members for a tenant."""
    # Verify user has access to this tenant
    user, role = require_tenant_access(tenant_id, current_user, db)

    # Get all user-tenant associations for this tenant
    user_tenants = (
        db.query(UserTenant, User)
        .join(User, UserTenant.user_id == User.id)
        .filter(UserTenant.tenant_id == tenant_id)
        .all()
    )

    team_members = [
        TeamMemberResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=user_tenant.role.value,
            joined_at=user.created_at,  # Using user created_at as proxy for joined_at
        )
        for user_tenant, user in user_tenants
    ]

    return TeamListResponse(
        team_members=team_members,
        total=len(team_members),
    )


@router.get("/recent-items", response_model=ItemListResponse)
def get_recent_items(
    tenant_id: UUID,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemListResponse:
    """Get recent items discovered across all sites for a tenant."""
    # Verify user has access to this tenant
    user, role = require_tenant_access(tenant_id, current_user, db)

    # Query recent items across all sites for this tenant
    items = (
        db.query(Item)
        .join(Site)
        .filter(Site.tenant_id == tenant_id)
        .order_by(desc(Item.discovered_at))
        .limit(limit)
        .all()
    )

    return ItemListResponse(
        items=[
            ItemResponse(
                id=item.id,
                site_id=item.site_id,
                url=item.url,
                canonical_url=item.canonical_url,
                title=item.title,
                published_at=item.published_at,
                discovered_at=item.discovered_at,
                source=item.source,
                meta_json=item.meta_json,
            )
            for item in items
        ],
        next_cursor=None,  # Simple list, no pagination cursor for dashboard
    )


@router.get("/recent-runs", response_model=RunListResponse)
def get_recent_runs(
    tenant_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunListResponse:
    """Get recent runs across all sites for a tenant."""
    # Verify user has access to this tenant
    user, role = require_tenant_access(tenant_id, current_user, db)

    # Query recent runs across all sites for this tenant
    runs = (
        db.query(Run)
        .join(Site)
        .filter(Site.tenant_id == tenant_id)
        .order_by(desc(Run.started_at))
        .limit(limit)
        .all()
    )

    return RunListResponse(
        runs=[
            RunResponse(
                id=run.id,
                site_id=run.site_id,
                status=run.status.value,
                method=run.method,
                pages_scanned=run.pages_scanned,
                duration_ms=run.duration_ms,
                diagnostics_json=run.diagnostics_json,
                started_at=run.started_at,
                finished_at=run.finished_at,
            )
            for run in runs
        ],
        total=len(runs),
    )

