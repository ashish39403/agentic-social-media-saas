from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from social_saas.config import Settings
from social_saas.database.url import application_database_url


def create_application_engine(settings: Settings) -> AsyncEngine | None:
    url = application_database_url(settings)
    if url is None:
        return None
    return create_async_engine(url, pool_pre_ping=True)
