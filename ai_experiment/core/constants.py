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


JSON_FORMAT_INSTRUCTION = "You will only provide a RFC8259 compliant" + \
" JSON response following this format without deviation:" + \
"""
```json
{
"completion": "Your generated text completion",
}
```
"""

CHATGPT_FUNCTIONS = [
        {
            "name": "answer_in_audio",
            "description": "If asked to answer in audio this function will be called.",
            "parameters": {
                "type": "object",
                "properties": {
                    "txt_completion": {
                        "type": "string",
                        "description": "The text completion",
                    },
                },
                "required": ["txt_completion"],
            },
        }
    ]
