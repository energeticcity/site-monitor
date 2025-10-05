"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Auth schemas
class MagicLinkRequest(BaseModel):
    """Magic link request."""

    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Magic link response."""

    success: bool
    message: str


class MagicLinkCallback(BaseModel):
    """Magic link callback."""

    token: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# User schemas
class UserBase(BaseModel):
    """User base schema."""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User create schema."""

    pass


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    created_at: datetime
    tenants: list["UserTenantResponse"] = []

    class Config:
        from_attributes = True


class UserTenantResponse(BaseModel):
    """User-tenant association response."""

    tenant_id: UUID
    tenant_name: str
    role: str

    class Config:
        from_attributes = True


# Tenant schemas
class TenantBase(BaseModel):
    """Tenant base schema."""

    name: str
    plan: str = "free"


class TenantCreate(TenantBase):
    """Tenant create schema."""

    pass


class TenantResponse(TenantBase):
    """Tenant response schema."""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Tenant list response."""

    tenants: list[TenantResponse]
    total: int


# Invite schemas
class InviteCreate(BaseModel):
    """Invite create schema."""

    email: EmailStr
    tenant_id: UUID
    role: str = Field(..., pattern="^(admin|member)$")


class InviteResponse(BaseModel):
    """Invite response schema."""

    id: UUID
    email: EmailStr
    role: str
    invite_link: str
    expires_at: datetime

    class Config:
        from_attributes = True


class InviteAccept(BaseModel):
    """Invite accept schema."""

    token: str
    name: Optional[str] = None


class InviteAcceptResponse(BaseModel):
    """Invite accept response."""

    success: bool
    tenant: TenantResponse


# Site schemas
class SiteBase(BaseModel):
    """Site base schema."""

    url: str
    profile_key: Optional[str] = None
    interval_minutes: int = 60
    keywords: Optional[list[str]] = None


class SiteCreate(SiteBase):
    """Site create schema."""

    pass


class SiteUpdate(BaseModel):
    """Site update schema."""

    url: Optional[str] = None
    profile_key: Optional[str] = None
    interval_minutes: Optional[int] = None
    keywords: Optional[list[str]] = None
    enabled: Optional[bool] = None


class SiteResponse(SiteBase):
    """Site response schema."""

    id: UUID
    tenant_id: UUID
    enabled: bool
    last_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SiteListResponse(BaseModel):
    """Site list response."""

    sites: list[SiteResponse]
    total: int


# Run schemas
class RunResponse(BaseModel):
    """Run response schema."""

    id: UUID
    site_id: UUID
    status: str
    method: Optional[str] = None
    pages_scanned: int
    duration_ms: Optional[int] = None
    diagnostics_json: Optional[dict[str, Any]] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    """Run list response."""

    runs: list[RunResponse]
    total: int


class RunTriggerResponse(BaseModel):
    """Run trigger response."""

    run_id: UUID
    status: str


# Item schemas
class ItemResponse(BaseModel):
    """Item response schema."""

    id: UUID
    site_id: UUID
    url: str
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    published_at: Optional[datetime] = None
    discovered_at: datetime
    source: Optional[str] = None
    meta_json: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """Item list response."""

    items: list[ItemResponse]
    next_cursor: Optional[str] = None


# Webhook schemas
class WebhookBase(BaseModel):
    """Webhook base schema."""

    endpoint_url: str
    secret: Optional[str] = None


class WebhookCreate(WebhookBase):
    """Webhook create schema."""

    pass


class WebhookResponse(WebhookBase):
    """Webhook response schema."""

    id: UUID
    tenant_id: UUID
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """Webhook list response."""

    webhooks: list[WebhookResponse]


# API Key schemas
class APIKeyCreate(BaseModel):
    """API key create schema."""

    name: str
    scopes: Optional[list[str]] = None


class APIKeyResponse(BaseModel):
    """API key response schema."""

    id: UUID
    name: Optional[str] = None
    token: Optional[str] = None  # Only shown on creation
    scopes: Optional[list[str]] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """API key list response."""

    keys: list[APIKeyResponse]


# Dashboard schemas
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""

    tenant_id: UUID
    tenant_name: str
    total_sites: int
    active_sites: int
    total_items: int
    items_this_week: int
    total_runs: int
    successful_runs_today: int
    failed_runs_today: int

    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    """Team member response."""

    user_id: UUID
    name: Optional[str] = None
    email: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Team list response."""

    team_members: list[TeamMemberResponse]
    total: int


# Health schema
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    database: str

