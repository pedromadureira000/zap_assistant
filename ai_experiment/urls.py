from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path("", include("ai_experiment.core.urls")),
    path("user/", include("ai_experiment.user.urls")),
    path("admin/", admin.site.urls),
]
