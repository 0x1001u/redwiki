"""Celery application for background tasks."""

from celery import Celery
from src.core.config import settings

celery_app = Celery(
    'agent_wiki_kb',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['src.services.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
)
