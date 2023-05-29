from django.urls import path
from ai_experiment.user.views import (
    obtain_auth_token
)

urlpatterns = [
    path('gettoken', obtain_auth_token, name='gettoken'),
]
