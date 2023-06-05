from django.urls import path

from ai_experiment.core.views import audio_transcription, chat_completion, conversational_agent, webhook, home

app_name = "core"
urlpatterns = [
    path("", home, name="home"),
    path("audio_transcription", audio_transcription, name="audio_transcription"),
    path("chat_completion", chat_completion, name="chat_completion"),
    path("conversational_agent/<str:agent>", conversational_agent, name="conversational_agent"),
    path("webhook/<uuid:webhook_id>", webhook, name="webhook"),
]
