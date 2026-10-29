from social_saas.worker.celery_app import celery_app


@celery_app.task(name="foundation.ping")  # type: ignore[untyped-decorator]
def ping() -> dict[str, str]:
    return {"status": "ok"}
