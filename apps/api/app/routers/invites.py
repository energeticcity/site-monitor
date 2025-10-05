"""Invites router."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, require_tenant_admin
from app.models import Invite, Role, Tenant, User, UserTenant
from app.schemas import InviteAccept, InviteAcceptResponse, InviteCreate, InviteResponse, TenantResponse
from app.utils.auth import create_invite_token, hash_token, verify_token

router = APIRouter(prefix="/v1/invites", tags=["invites"])


@router.post("", response_model=InviteResponse)
def create_invite(
    invite: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InviteResponse:
    """Create an invite (admin only)."""
    # Verify user is admin of the tenant
    _ = require_tenant_admin(invite.tenant_id, current_user, db)

    # Validate role
    if invite.role not in ["admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    # Check if user already exists and is member of tenant
    existing_user = db.query(User).filter(User.email == invite.email).first()
    if existing_user:
        existing_membership = (
            db.query(UserTenant)
            .filter(
                UserTenant.user_id == existing_user.id,
                UserTenant.tenant_id == invite.tenant_id,
            )
            .first()
        )
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this tenant",
            )

    # Create invite
    token = create_invite_token()
    new_invite = Invite(
        email=invite.email,
        tenant_id=invite.tenant_id,
        role=Role.ADMIN if invite.role == "admin" else Role.MEMBER,
        token_hash=hash_token(token),
        expires_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
    )
    db.add(new_invite)
    db.commit()
    db.refresh(new_invite)

    invite_link = f"{settings.magic_link_base_url}/auth/invite?token={token}"

    return InviteResponse(
        id=new_invite.id,
        email=new_invite.email,
        role=new_invite.role.value,
        invite_link=invite_link,
        expires_at=new_invite.expires_at,
    )


@router.post("/accept", response_model=InviteAcceptResponse)
def accept_invite(
    accept: InviteAccept,
    db: Session = Depends(get_db),
) -> InviteAcceptResponse:
    """Accept an invite."""
    # Find invite by checking token against all hashed tokens
    invites = db.query(Invite).filter(Invite.accepted_at.is_(None)).all()

    invite = None
    for inv in invites:
        if verify_token(accept.token, inv.token_hash):
            invite = inv
            break

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite",
        )

    # Check if expired
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite has expired",
        )

    # Find or create user
    user = db.query(User).filter(User.email == invite.email).first()
    if not user:
        user = User(
            email=invite.email,
            name=accept.name,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.flush()

    # Create user-tenant association
    user_tenant = UserTenant(
        user_id=user.id,
        tenant_id=invite.tenant_id,
        role=invite.role,
    )
    db.add(user_tenant)

    # Mark invite as accepted
    invite.accepted_at = datetime.utcnow()

    db.commit()

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == invite.tenant_id).first()

    return InviteAcceptResponse(
        success=True,
        tenant=TenantResponse(
            id=tenant.id,
            name=tenant.name,
            plan=tenant.plan,
            created_at=tenant.created_at,
        ),
    )

