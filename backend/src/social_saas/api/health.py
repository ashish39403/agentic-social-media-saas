from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from social_saas.config import Settings, get_settings
from social_saas.database.engine import create_application_engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@router.get("/ready", response_model=None)
async def readiness(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any] | JSONResponse:
    checks: dict[str, str] = {}

    engine = create_application_engine(settings)
    if engine is None:
        checks["database"] = "not_configured"
    else:
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:  # The public response must not leak driver or credential details.
            checks["database"] = "unavailable"
        finally:
            await engine.dispose()

    redis = Redis.from_url(settings.redis_url, socket_connect_timeout=1, decode_responses=True)
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "unavailable"
    finally:
        await redis.aclose()

    if all(value == "ok" for value in checks.values()):
        return {"status": "ready", "checks": checks}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not_ready", "checks": checks},
    )
