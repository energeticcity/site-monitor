"""Database seeding script - fresh version to bypass Railway cache."""

import hashlib
import secrets
from datetime import datetime, timedelta

from app.config import settings
from app.database import SessionLocal
from app.models import Invite, Tenant, User, UserTenant


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

        # Associate super admin with demo tenant - using lowercase string directly
        super_admin_assoc = UserTenant(
            user_id=super_admin.id, 
            tenant_id=demo_tenant.id, 
            role="super_admin"  # LOWERCASE STRING
        )
        db.add(super_admin_assoc)
        db.flush()  # Flush to catch errors early
        print("✓ Associated Super Admin with Demo Tenant")

        db.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\nSuper Admin: {super_admin.email}")
        print("Demo Tenant: Demo Tenant")
        print("\n✨ Ready to login!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
