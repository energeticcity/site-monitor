"""Tenants router."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_super_admin
from app.models import Tenant, User
from app.schemas import TenantCreate, TenantListResponse, TenantResponse

router = APIRouter(prefix="/v1/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
) -> TenantResponse:
    """Create a new tenant (super_admin only)."""
    new_tenant = Tenant(
        name=tenant.name,
        plan=tenant.plan,
        created_at=datetime.utcnow(),
    )
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)

    return TenantResponse(
        id=new_tenant.id,
        name=new_tenant.name,
        plan=new_tenant.plan,
        created_at=new_tenant.created_at,
    )


@router.get("", response_model=TenantListResponse)
def list_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
) -> TenantListResponse:
    """List all tenants (super_admin only)."""
    tenants = db.query(Tenant).all()

    return TenantListResponse(
        tenants=[
            TenantResponse(
                id=t.id,
                name=t.name,
                plan=t.plan,
                created_at=t.created_at,
            )
            for t in tenants
        ],
        total=len(tenants),
    )

