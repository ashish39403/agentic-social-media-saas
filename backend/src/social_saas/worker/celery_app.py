from __future__ import annotations

from celery import Celery

from social_saas.config import get_settings

settings = get_settings()

celery_app = Celery(
    "social_saas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["social_saas.worker.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
