"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sitewatcher"
    test_database_url: str = "postgresql://postgres:postgres@localhost:5432/sitewatcher_test"

    # JWT
    jwt_secret: str = "change-me-to-secure-random-string-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 43200  # 30 days

    # Worker
    worker_base_url: str = "https://your-worker.workers.dev"

    # Email
    email_from: str = "no-reply@sitewatcher.app"
    postmark_token: str = ""

    # Magic Link
    magic_link_base_url: str = "http://localhost:3000"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Testing
    e2e_use_real_worker: bool = False
    skip_contract_tests: bool = False

    # Super Admin
    super_admin_email: str = "admin@sitewatcher.app"
    super_admin_name: str = "Super Admin"


settings = Settings()

