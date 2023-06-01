import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_experiment.settings")
app = Celery("ai_experiment")
app.config_from_object(settings, namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {"ai_experiment.core.tasks.*": {"queue": "send_completion_to_user"}}
