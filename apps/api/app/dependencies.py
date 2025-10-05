"""FastAPI dependencies."""

from typing import Optional
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User, UserTenant
from app.utils.auth import decode_jwt_token


def get_current_user(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    token = None

    # Try cookie first
    if access_token:
        token = access_token
    # Then try Authorization header
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_jwt_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_super_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Require super admin role."""
    # Check if user has super_admin role in any tenant
    is_super_admin = (
        db.query(UserTenant)
        .filter(
            UserTenant.user_id == current_user.id,
            UserTenant.role == Role.SUPER_ADMIN,
        )
        .first()
    )

    if not is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )

    return current_user


def get_user_tenant_role(
    user: User,
    tenant_id: UUID,
    db: Session,
) -> Optional[Role]:
    """Get user's role in a tenant."""
    user_tenant = (
        db.query(UserTenant)
        .filter(
            UserTenant.user_id == user.id,
            UserTenant.tenant_id == tenant_id,
        )
        .first()
    )

    if not user_tenant:
        return None

    return user_tenant.role


def require_tenant_access(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> tuple[User, Role]:
    """Require user to have access to a tenant."""
    # Super admins have access to all tenants
    is_super_admin = (
        db.query(UserTenant)
        .filter(
            UserTenant.user_id == current_user.id,
            UserTenant.role == Role.SUPER_ADMIN,
        )
        .first()
    )

    if is_super_admin:
        return current_user, Role.SUPER_ADMIN

    # Check if user has access to this tenant
    role = get_user_tenant_role(current_user, tenant_id, db)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant not allowed",
        )

    return current_user, role


def require_tenant_admin(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Require user to be an admin of a tenant."""
    user, role = require_tenant_access(tenant_id, current_user, db)

    if role not in [Role.SUPER_ADMIN, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user

