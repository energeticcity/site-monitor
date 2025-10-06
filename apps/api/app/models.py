"""Database models."""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Role(str, enum.Enum):
    """User roles."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MEMBER = "member"


class RunStatus(str, enum.Enum):
    """Run status."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class Tenant(Base):
    """Tenant model."""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    plan = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sites = relationship("Site", back_populates="tenant", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="tenant", cascade="all, delete-orphan")
    invites = relationship("Invite", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_tenants = relationship("UserTenant", back_populates="user", cascade="all, delete-orphan")


class UserTenant(Base):
    """User-Tenant association with role."""

    __tablename__ = "user_tenants"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    role = Column(Enum(Role, values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_tenants")
    tenant = relationship("Tenant")


class Site(Base):
    """Site model."""

    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    url = Column(String, nullable=False)
    profile_key = Column(String)
    keywords = Column(ARRAY(Text))
    enabled = Column(Boolean, default=True)
    interval_minutes = Column(Integer, default=60)
    last_run_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="sites")
    runs = relationship("Run", back_populates="site", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="site", cascade="all, delete-orphan")


class Run(Base):
    """Run model."""

    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    status = Column(Enum(RunStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=RunStatus.RUNNING)
    method = Column(String)  # 'profile' or 'discover'
    pages_scanned = Column(Integer, default=0)
    duration_ms = Column(Integer)
    diagnostics_json = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

    # Relationships
    site = relationship("Site", back_populates="runs")


class Item(Base):
    """Item model."""

    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("site_id", "canonical_url", name="uix_site_canonical"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    url = Column(String, nullable=False)
    canonical_url = Column(String)
    title = Column(String)
    published_at = Column(DateTime)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String)  # 'feed', 'html', 'sitemap'
    meta_json = Column(JSON)

    # Relationships
    site = relationship("Site", back_populates="items")


class Webhook(Base):
    """Webhook model."""

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    endpoint_url = Column(String, nullable=False)
    secret = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="webhooks")


class APIKey(Base):
    """API Key model."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String)
    token_hash = Column(String, nullable=False, unique=True)
    scopes = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)

    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")


class Invite(Base):
    """Invite model."""

    __tablename__ = "invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    role = Column(Enum(Role, values_callable=lambda x: [e.value for e in x]), nullable=False)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="invites")

