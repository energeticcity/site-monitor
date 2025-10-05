"""Webhooks router."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_tenant_admin
from app.models import User, Webhook
from app.schemas import WebhookCreate, WebhookListResponse, WebhookResponse

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WebhookResponse:
    """Create a webhook."""
    # Get user's first tenant (admin only)
    user_tenant = current_user.user_tenants[0] if current_user.user_tenants else None
    if not user_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant",
        )

    # Verify user is admin
    _ = require_tenant_admin(user_tenant.tenant_id, current_user, db)

    new_webhook = Webhook(
        tenant_id=user_tenant.tenant_id,
        endpoint_url=webhook.endpoint_url,
        secret=webhook.secret,
        created_at=datetime.utcnow(),
    )
    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)

    return WebhookResponse(
        id=new_webhook.id,
        tenant_id=new_webhook.tenant_id,
        endpoint_url=new_webhook.endpoint_url,
        secret=new_webhook.secret,
        active=new_webhook.active,
        created_at=new_webhook.created_at,
    )


@router.get("", response_model=WebhookListResponse)
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WebhookListResponse:
    """List webhooks for user's tenant."""
    # Get user's tenants
    tenant_ids = [ut.tenant_id for ut in current_user.user_tenants]

    webhooks = db.query(Webhook).filter(Webhook.tenant_id.in_(tenant_ids)).all()

    return WebhookListResponse(
        webhooks=[
            WebhookResponse(
                id=w.id,
                tenant_id=w.tenant_id,
                endpoint_url=w.endpoint_url,
                secret=w.secret,
                active=w.active,
                created_at=w.created_at,
            )
            for w in webhooks
        ]
    )

