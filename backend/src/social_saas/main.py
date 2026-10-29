from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from social_saas.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Social Media SaaS API", version="0.1.0")

    @app.middleware("http")
    async def correlation_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    app.include_router(health_router, prefix="/api/v1")
    return app


app = create_app()
