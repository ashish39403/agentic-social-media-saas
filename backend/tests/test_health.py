import httpx
import pytest

from social_saas.config import Settings, get_settings
from social_saas.main import create_app


@pytest.mark.asyncio
async def test_liveness_is_safe_and_successful() -> None:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-social-media-saas-api"}
    assert response.headers["x-request-id"]


@pytest.mark.asyncio
async def test_readiness_reports_missing_dependencies_without_details() -> None:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(
        database_url=None,
        redis_url="redis://127.0.0.1:1/0",
        _env_file=None,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": "not_configured", "redis": "unavailable"},
    }
