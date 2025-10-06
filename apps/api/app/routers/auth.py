"""Auth router."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    MagicLinkCallback,
    MagicLinkRequest,
    MagicLinkResponse,
    TokenResponse,
    UserResponse,
    UserTenantResponse,
)
from app.config import settings
from app.utils.auth import create_jwt_token, create_magic_link_token, hash_token, verify_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# In-memory store for dev magic links (in production, use Redis or database)
magic_links: dict[str, str] = {}


@router.post("/magic-link", response_model=MagicLinkResponse)
def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db),
) -> MagicLinkResponse:
    """Request magic link (dev stub - logs to console)."""
    # Create token
    token = create_magic_link_token()
    token_hash = hash_token(token)

    # Store token with email (in production, store in DB with expiry)
    magic_links[token] = request.email

    # In dev, log the link to console
    magic_link = f"http://localhost:3000/auth/callback?token={token}"
    print(f"\n🔗 Magic Link for {request.email}:")
    print(f"   {magic_link}\n")

    return MagicLinkResponse(
        success=True,
        message=f"Magic link sent to {request.email} (check console in dev mode)",
    )


@router.post("/magic-link/callback", response_model=TokenResponse)
def magic_link_callback(
    callback: MagicLinkCallback,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange magic link token for JWT."""
    # Verify token exists
    email = magic_links.get(callback.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, created_at=datetime.utcnow())
        db.add(user)
        db.commit()
        db.refresh(user)

    # Remove used token
    del magic_links[callback.token]

    # Create JWT
    jwt_token = create_jwt_token(str(user.id))

    # Set httpOnly cookie
    # Use secure=True for production (HTTPS), False for local development
    is_production = settings.magic_link_base_url.startswith("https://")
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=is_production,
        samesite="none" if is_production else "lax",  # "none" required for cross-site cookies with secure=True
        max_age=60 * 60 * 24 * 30,  # 30 days
    )

    # Get user tenants
    user_tenants = []
    for ut in user.user_tenants:
        user_tenants.append(
            UserTenantResponse(
                tenant_id=ut.tenant_id,
                tenant_name=ut.tenant.name,
                role=ut.role.value,
            )
        )

    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        tenants=user_tenants,
    )

    return TokenResponse(
        access_token=jwt_token,
        user=user_response,
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Get current user info."""
    # Get user tenants
    user_tenants = []
    for ut in current_user.user_tenants:
        user_tenants.append(
            UserTenantResponse(
                tenant_id=ut.tenant_id,
                tenant_name=ut.tenant.name,
                role=ut.role.value,
            )
        )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        tenants=user_tenants,
    )

