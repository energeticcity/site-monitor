"""Pytest configuration and fixtures."""

from datetime import datetime
from typing import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Role, Tenant, User, UserTenant
from app.utils.auth import create_jwt_token

# Use test database
TEST_DATABASE_URL = settings.test_database_url
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create test database session."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create test client."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def super_admin_user(db: Session) -> User:
    """Create a super admin user."""
    user = User(
        email="super@test.com",
        name="Super Admin",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_tenant(db: Session) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Tenant",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def super_admin_with_tenant(db: Session, super_admin_user: User, test_tenant: Tenant) -> User:
    """Create super admin associated with tenant."""
    user_tenant = UserTenant(
        user_id=super_admin_user.id,
        tenant_id=test_tenant.id,
        role=Role.SUPER_ADMIN,
    )
    db.add(user_tenant)
    db.commit()

    # Refresh to load relationships
    db.refresh(super_admin_user)
    return super_admin_user


@pytest.fixture
def admin_user(db: Session, test_tenant: Tenant) -> User:
    """Create an admin user."""
    user = User(
        email="admin@test.com",
        name="Admin User",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()

    user_tenant = UserTenant(
        user_id=user.id,
        tenant_id=test_tenant.id,
        role=Role.ADMIN,
    )
    db.add(user_tenant)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def member_user(db: Session, test_tenant: Tenant) -> User:
    """Create a member user."""
    user = User(
        email="member@test.com",
        name="Member User",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()

    user_tenant = UserTenant(
        user_id=user.id,
        tenant_id=test_tenant.id,
        role=Role.MEMBER,
    )
    db.add(user_tenant)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(super_admin_user: User) -> dict[str, str]:
    """Create auth headers with JWT."""
    token = create_jwt_token(str(super_admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict[str, str]:
    """Create auth headers for admin user."""
    token = create_jwt_token(str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def member_auth_headers(member_user: User) -> dict[str, str]:
    """Create auth headers for member user."""
    token = create_jwt_token(str(member_user.id))
    return {"Authorization": f"Bearer {token}"}

