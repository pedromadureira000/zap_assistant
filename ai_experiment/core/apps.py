from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_experiment.core"

    def ready(self):
        import ai_experiment.core.signals
