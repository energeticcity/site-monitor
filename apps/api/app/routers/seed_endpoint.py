"""One-time seed endpoint for manual database seeding."""

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.database import engine, get_db
from app.dependencies import require_super_admin

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/seed-database")
@router.post("/seed-database")
def seed_database_endpoint() -> dict:
    """
    One-time endpoint to seed the database.
    Call this once to create super admin and demo tenant.
    """
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count > 0:
            return {"message": "Database already seeded", "user_count": count}
        
        # Create user
        conn.execute(text("""
            INSERT INTO users (id, email, name, created_at) 
            VALUES (gen_random_uuid(), 'areaburn@moosemediafsj.ca', 'Adam Reaburn', NOW())
        """))
        
        # Create tenant
        conn.execute(text("""
            INSERT INTO tenants (id, name, plan, created_at) 
            VALUES (gen_random_uuid(), 'Demo Tenant', 'free', NOW())
        """))
        
        # Link them
        conn.execute(text("""
            INSERT INTO user_tenants (user_id, tenant_id, role)
            SELECT u.id, t.id, 'super_admin'
            FROM users u, tenants t
            WHERE u.email = 'areaburn@moosemediafsj.ca' 
            AND t.name = 'Demo Tenant'
            LIMIT 1
        """))
        
        conn.commit()
    
    return {
        "message": "✅ Database seeded successfully!",
        "super_admin": "areaburn@moosemediafsj.ca",
        "tenant": "Demo Tenant"
    }
