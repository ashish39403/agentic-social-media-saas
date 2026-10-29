from __future__ import annotations

from social_saas.config import Settings


def normalize_async_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def application_database_url(settings: Settings) -> str | None:
    if settings.database_url is None:
        return None
    return normalize_async_database_url(settings.database_url)


def migration_database_url(settings: Settings) -> str:
    if settings.database_url_unpooled is None:
        raise RuntimeError("DATABASE_URL_UNPOOLED is required for Alembic migrations")
    return normalize_async_database_url(settings.database_url_unpooled)
