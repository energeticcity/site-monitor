"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api_keys, auth, dashboard, invites, sites, tenants, webhooks
from app.database import engine
from sqlalchemy import text

app = FastAPI(
    title="SiteWatcher API",
    description="Multi-tenant SaaS for detecting new posts on websites",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(invites.router)
app.include_router(sites.router)
app.include_router(webhooks.router)
app.include_router(api_keys.router)
app.include_router(dashboard.router)


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    # Test database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "database": db_status,
    }


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "SiteWatcher API",
        "version": "0.1.0",
        "docs": "/docs",
    }

