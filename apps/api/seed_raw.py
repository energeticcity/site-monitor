"""Database seeding using RAW SQL to bypass SQLAlchemy cache."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import text

from app.config import settings
from app.database import engine


def seed_database() -> None:
    """Seed database with initial data using raw SQL."""
    print("🌱 Seeding database with RAW SQL...")

    with engine.connect() as conn:
        # Check if super admin already exists
        result = conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": settings.super_admin_email}
        )
        existing = result.fetchone()
        
        if existing:
            print(f"✓ Super Admin already exists: {settings.super_admin_email}")
            conn.commit()
            return

        # Create Super Admin user
        user_id = str(uuid4())
        conn.execute(
            text("""
                INSERT INTO users (id, email, name, created_at)
                VALUES (:user_id, :email, :name, :created_at)
            """),
            {
                "user_id": user_id,
                "email": settings.super_admin_email,
                "name": settings.super_admin_name,
                "created_at": datetime.utcnow()
            }
        )
        print(f"✓ Created Super Admin: {settings.super_admin_email}")

        # Create demo tenant
        tenant_id = str(uuid4())
        conn.execute(
            text("""
                INSERT INTO tenants (id, name, plan, created_at)
                VALUES (:tenant_id, :name, :plan, :created_at)
            """),
            {
                "tenant_id": tenant_id,
                "name": "Demo Tenant",
                "plan": "free",
                "created_at": datetime.utcnow()
            }
        )
        print(f"✓ Created Demo Tenant: Demo Tenant")

        # Associate super admin with demo tenant - LOWERCASE "super_admin"
        conn.execute(
            text("""
                INSERT INTO user_tenants (user_id, tenant_id, role)
                VALUES (:user_id, :tenant_id, :role)
            """),
            {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": "super_admin"  # LOWERCASE!
            }
        )
        print("✓ Associated Super Admin with Demo Tenant")

        conn.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\nSuper Admin: {settings.super_admin_email}")
        print("Demo Tenant: Demo Tenant")
        print("\n✨ Ready to login!")


if __name__ == "__main__":
    seed_database()
