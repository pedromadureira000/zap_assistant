from django.db import models

from ai_experiment.core.serializers import WebhookConversationSerializer


class frequencyChoices(models.TextChoices):
    DAILY = "daily", "Diariamente"
    WEEKLY = "weekly", "Semanalmente"
    BIWEEKLY = "biweekly", "Quinzenalmente"
    MONTHLY = "monthly", "Mensalmente"


class dayOfWeekChoices(models.TextChoices):
    MONDAY = "monday", "Segunda-feira"
    TUESDAY = "tuesday", "Terça-feira"
    WEDNESDAY = "wednesday", "Quarta-feira"
    THURSDAY = "thursday", "Quinta-feira"
    FRIDAY = "friday", "Sexta-feira"
    SATURDAY = "saturday", "Sábado"
    SUNDAY = "sunday", "Domingo"


WEBHOOK_SERIALIZERS = {
    "conversation": WebhookConversationSerializer,
    "extendedTextMessage": WebhookConversationSerializer,
    "audioMessage": WebhookConversationSerializer,
}
