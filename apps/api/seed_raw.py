"""Database seeding using RAW SQL to bypass SQLAlchemy cache."""

from datetime import datetime
from uuid import uuid4

from app.config import settings
from app.database import engine


def seed_database() -> None:
    """Seed database with initial data using raw SQL."""
    print("🌱 Seeding database with RAW SQL...")

    with engine.connect() as conn:
        # Check if super admin already exists
        result = conn.execute(
            f"SELECT id FROM users WHERE email = '{settings.super_admin_email}'"
        )
        existing = result.fetchone()
        
        if existing:
            print(f"✓ Super Admin already exists: {settings.super_admin_email}")
            conn.commit()
            return

        # Create Super Admin user
        user_id = str(uuid4())
        conn.execute(
            f"""
            INSERT INTO users (id, email, name, created_at)
            VALUES ('{user_id}', '{settings.super_admin_email}', '{settings.super_admin_name}', '{datetime.utcnow().isoformat()}')
            """
        )
        print(f"✓ Created Super Admin: {settings.super_admin_email}")

        # Create demo tenant
        tenant_id = str(uuid4())
        conn.execute(
            f"""
            INSERT INTO tenants (id, name, plan, created_at)
            VALUES ('{tenant_id}', 'Demo Tenant', 'free', '{datetime.utcnow().isoformat()}')
            """
        )
        print(f"✓ Created Demo Tenant: Demo Tenant")

        # Associate super admin with demo tenant - LOWERCASE "super_admin"
        conn.execute(
            f"""
            INSERT INTO user_tenants (user_id, tenant_id, role)
            VALUES ('{user_id}', '{tenant_id}', 'super_admin')
            """
        )
        print("✓ Associated Super Admin with Demo Tenant")

        conn.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\nSuper Admin: {settings.super_admin_email}")
        print("Demo Tenant: Demo Tenant")
        print("\n✨ Ready to login!")


if __name__ == "__main__":
    seed_database()
