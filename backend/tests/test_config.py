import pytest

from social_saas.config import Settings
from social_saas.database.url import application_database_url, migration_database_url


def test_application_url_is_normalized_for_asyncpg() -> None:
    settings = Settings(database_url="postgresql://host/db", _env_file=None)
    assert application_database_url(settings) == "postgresql+asyncpg://host/db"


def test_migrations_require_direct_url() -> None:
    settings = Settings(database_url_unpooled=None, _env_file=None)
    with pytest.raises(RuntimeError, match="DATABASE_URL_UNPOOLED"):
        migration_database_url(settings)
