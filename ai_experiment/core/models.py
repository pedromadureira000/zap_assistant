import uuid

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


JSON_FORMAT_INSTRUCTION =  "You will always answer as JSON, following this format without deviation: `{\"completion\": \"Your generated text completion\"}`. For example: [{'role': 'user', 'content': 'Has man ever been to the moon? For real?'},{'role': 'assistant', 'content': '{\"completion\": \"Yes, man has actually been to the moon! The Apollo 11 mission landed on the moon on July 20, 1969. It was a historic achievement for humanity and a significant milestone in space exploration. 🚀🌕\"}'}]"

class Base(models.Model):
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)

    class Meta:
        abstract = True


class Conversation(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="conversations")
    agent = models.ForeignKey("Agent", on_delete=models.CASCADE)
    messages = ArrayField(models.JSONField(), default=list)
    mega_instance = models.ForeignKey(
        "mega_api.MegaAPIInstance",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    processing_request = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "mega_instance"),)

    def save(self, *args, **kwargs):
        if self.agent != Conversation.objects.get(id=self.id).agent:
            self.messages = []
        super().save(*args, **kwargs)


class Agent(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome", max_length=255, unique=True)
    description = models.TextField("Descrição", blank=True)
    system_instruction = models.TextField("system instruction")

    def __str__(self):
        return self.name
