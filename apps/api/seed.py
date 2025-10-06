"""Database seeding script for production deployment."""

import hashlib
import secrets
from datetime import datetime, timedelta

from app.config import settings
from app.database import SessionLocal
from app.models import Invite, Tenant, User, UserTenant


def create_invite_token() -> str:
    """Create an invite token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token using SHA256."""
    return hashlib.sha256(token.encode()).hexdigest()


def seed_database() -> None:
    """Seed database with initial data."""
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # Check if super admin already exists
        existing_user = db.query(User).filter(User.email == settings.super_admin_email).first()
        if existing_user:
            print(f"✓ Super Admin already exists: {settings.super_admin_email}")
            return

        # Create Super Admin user
        super_admin = User(
            email=settings.super_admin_email,
            name=settings.super_admin_name,
            created_at=datetime.utcnow(),
        )
        db.add(super_admin)
        db.flush()
        print(f"✓ Created Super Admin: {super_admin.email}")

        # Create demo tenant
        demo_tenant = Tenant(name="Demo Tenant", plan="free", created_at=datetime.utcnow())
        db.add(demo_tenant)
        db.flush()
        print(f"✓ Created Demo Tenant: {demo_tenant.name}")

        # Associate super admin with demo tenant
        super_admin_assoc = UserTenant(
            user_id=super_admin.id, tenant_id=demo_tenant.id, role="super_admin"
        )
        db.add(super_admin_assoc)
        print("✓ Associated Super Admin with Demo Tenant")

        # Create demo admin invite
        admin_token = create_invite_token()
        admin_invite = Invite(
            email="demo-admin@sitewatcher.app",
            tenant_id=demo_tenant.id,
            role="admin",
            token_hash=hash_token(admin_token),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
        )
        db.add(admin_invite)
        print(f"✓ Created Admin Invite for demo-admin@sitewatcher.app")
        print(f"  Invite token: {admin_token}")

        # Create demo member invite
        member_token = create_invite_token()
        member_invite = Invite(
            email="demo-member@sitewatcher.app",
            tenant_id=demo_tenant.id,
            role="member",
            token_hash=hash_token(member_token),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
        )
        db.add(member_invite)
        print(f"✓ Created Member Invite for demo-member@sitewatcher.app")
        print(f"  Invite token: {member_token}")

        db.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\nSuper Admin: {super_admin.email}")
        print("Demo Tenant: Demo Tenant")
        print("\nInvites:")
        print(f"  Admin: {settings.magic_link_base_url}/auth/invite?token={admin_token}")
        print(f"  Member: {settings.magic_link_base_url}/auth/invite?token={member_token}")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
