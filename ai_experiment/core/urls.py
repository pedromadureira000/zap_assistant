from django.urls import path

from ai_experiment.core.views import trial_success, webhook, home

app_name = "core"
urlpatterns = [
    path("", home, name="home"),
    path("trial_success", trial_success, name="home"),
    path("webhook/<uuid:webhook_id>", webhook, name="webhook"),
]
