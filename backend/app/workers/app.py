from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "signal",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    accept_content=["json"],
    result_expires=3600,
    result_serializer="json",
    task_serializer="json",
    timezone="UTC",
)
