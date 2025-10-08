"""Sites router."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_tenant_access, require_tenant_admin
from app.models import Item, Role, Run, RunStatus, Site, User
from app.schemas import (
    ItemListResponse,
    ItemResponse,
    RunListResponse,
    RunResponse,
    RunTriggerResponse,
    SiteCreate,
    SiteListResponse,
    SiteResponse,
)
from app.services.worker_client import WorkerClient, WorkerClientError, get_worker_client

router = APIRouter(prefix="/v1/sites", tags=["sites"])


@router.post("", response_model=SiteResponse)
def create_site(
    site: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteResponse:
    """Create a new site."""
    # Get user's first tenant (or require tenant_id in request in production)
    user_tenant = current_user.user_tenants[0] if current_user.user_tenants else None
    if not user_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant",
        )

    # Verify user is admin
    if user_tenant.role == Role.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to create sites",
        )

    new_site = Site(
        tenant_id=user_tenant.tenant_id,
        url=site.url,
        profile_key=site.profile_key,
        interval_minutes=site.interval_minutes,
        keywords=site.keywords,
        created_at=datetime.utcnow(),
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)

    return SiteResponse(
        id=new_site.id,
        tenant_id=new_site.tenant_id,
        url=new_site.url,
        profile_key=new_site.profile_key,
        keywords=new_site.keywords,
        enabled=new_site.enabled,
        interval_minutes=new_site.interval_minutes,
        last_run_at=new_site.last_run_at,
        created_at=new_site.created_at,
    )


@router.get("", response_model=SiteListResponse)
def list_sites(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteListResponse:
    """List sites for user's tenant."""
    # Get user's tenants
    tenant_ids = [ut.tenant_id for ut in current_user.user_tenants]

    # Query sites
    query = db.query(Site).filter(Site.tenant_id.in_(tenant_ids))
    total = query.count()

    sites = query.order_by(desc(Site.created_at)).offset((page - 1) * limit).limit(limit).all()

    return SiteListResponse(
        sites=[
            SiteResponse(
                id=s.id,
                tenant_id=s.tenant_id,
                url=s.url,
                profile_key=s.profile_key,
                keywords=s.keywords,
                enabled=s.enabled,
                interval_minutes=s.interval_minutes,
                last_run_at=s.last_run_at,
                created_at=s.created_at,
            )
            for s in sites
        ],
        total=total,
    )


@router.get("/{site_id}", response_model=SiteResponse)
def get_site(
    site_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteResponse:
    """Get site details."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Verify access
    _ = require_tenant_access(site.tenant_id, current_user, db)

    return SiteResponse(
        id=site.id,
        tenant_id=site.tenant_id,
        url=site.url,
        profile_key=site.profile_key,
        keywords=site.keywords,
        enabled=site.enabled,
        interval_minutes=site.interval_minutes,
        last_run_at=site.last_run_at,
        created_at=site.created_at,
    )


@router.post("/{site_id}/run", response_model=RunTriggerResponse)
def trigger_run(
    site_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunTriggerResponse:
    """Trigger a discovery run."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Verify user is admin
    user, role = require_tenant_access(site.tenant_id, current_user, db)
    if role == Role.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to trigger runs",
        )

    # Create run record
    run = Run(
        site_id=site.id,
        status=RunStatus.RUNNING,
        method="profile" if site.profile_key else "discover",
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Call Worker
    start_time = datetime.utcnow()
    try:
        with get_worker_client() as worker:
            if site.profile_key == "rcmp_fsj":
                response = worker.rcmp_fsj()
            else:
                response = worker.discover(site.url)

        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Process results and create items
        new_items_count = 0
        if response.links:
            for link in response.links:
                # Insert item; ignore if (site_id, canonical_url) already exists
                stmt = (
                    insert(Item)
                    .values(
                        site_id=site.id,
                        url=link,
                        canonical_url=link,
                        source=response.source,
                        discovered_at=datetime.utcnow(),
                    )
                    .on_conflict_do_nothing(index_elements=[Item.site_id, Item.canonical_url])
                )
                result = db.execute(stmt)
                # rowcount is 1 if inserted, 0 if skipped due to conflict
                if getattr(result, "rowcount", 0) == 1:
                    new_items_count += 1

        # Update run
        run.status = RunStatus.SUCCESS
        run.pages_scanned = response.count
        run.duration_ms = duration_ms
        run.diagnostics_json = response.diagnostics
        run.finished_at = end_time

        # Update site
        site.last_run_at = end_time

        db.commit()

        # TODO: Trigger notifications (implement in next iteration)

        return RunTriggerResponse(
            run_id=run.id,
            status="success",
        )

    except WorkerClientError as e:
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Update run as error
        run.status = RunStatus.ERROR
        run.duration_ms = duration_ms
        run.diagnostics_json = {
            "error": str(e),
            "status_code": e.status_code,
        }
        run.finished_at = end_time

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Worker error",
                "error": str(e),
                "status_code": e.status_code,
                "worker_response": e.response,
            },
        )


@router.get("/{site_id}/items", response_model=ItemListResponse)
def list_items(
    site_id: UUID,
    cursor: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemListResponse:
    """List items for a site (cursor pagination)."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Verify access
    _ = require_tenant_access(site.tenant_id, current_user, db)

    # Query items
    query = db.query(Item).filter(Item.site_id == site_id)

    if cursor:
        # Cursor is the last item ID
        query = query.filter(Item.id < UUID(cursor))

    items = query.order_by(desc(Item.discovered_at)).limit(limit + 1).all()

    # Check if there are more items
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = str(items[-1].id) if items and has_more else None

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
        next_cursor=next_cursor,
    )


@router.get("/{site_id}/runs", response_model=RunListResponse)
def list_runs(
    site_id: UUID,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunListResponse:
    """List runs for a site."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Verify access
    _ = require_tenant_access(site.tenant_id, current_user, db)

    # Query runs
    query = db.query(Run).filter(Run.site_id == site_id)
    total = query.count()

    runs = query.order_by(desc(Run.started_at)).offset((page - 1) * limit).limit(limit).all()

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
        total=total,
    )

