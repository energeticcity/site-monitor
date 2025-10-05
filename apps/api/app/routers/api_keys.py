"""API Keys router."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_tenant_admin
from app.models import APIKey, User
from app.schemas import APIKeyCreate, APIKeyListResponse, APIKeyResponse
from app.utils.auth import create_api_key, hash_token

router = APIRouter(prefix="/v1/keys", tags=["api-keys"])


@router.post("", response_model=APIKeyResponse)
def create_api_key(
    key: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIKeyResponse:
    """Create an API key."""
    # Get user's first tenant (admin only)
    user_tenant = current_user.user_tenants[0] if current_user.user_tenants else None
    if not user_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant",
        )

    # Verify user is admin
    _ = require_tenant_admin(user_tenant.tenant_id, current_user, db)

    # Create token
    token = create_api_key()

    new_key = APIKey(
        tenant_id=user_tenant.tenant_id,
        name=key.name,
        token_hash=hash_token(token),
        scopes=key.scopes,
        created_at=datetime.utcnow(),
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return APIKeyResponse(
        id=new_key.id,
        name=new_key.name,
        token=token,  # Only shown on creation
        scopes=new_key.scopes,
        created_at=new_key.created_at,
        last_used_at=new_key.last_used_at,
    )


@router.get("", response_model=APIKeyListResponse)
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIKeyListResponse:
    """List API keys for user's tenant."""
    # Get user's tenants
    tenant_ids = [ut.tenant_id for ut in current_user.user_tenants]

    keys = db.query(APIKey).filter(APIKey.tenant_id.in_(tenant_ids)).all()

    return APIKeyListResponse(
        keys=[
            APIKeyResponse(
                id=k.id,
                name=k.name,
                scopes=k.scopes,
                created_at=k.created_at,
                last_used_at=k.last_used_at,
            )
            for k in keys
        ]
    )

