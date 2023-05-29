import uuid

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


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

    def save(self, *args, **kwargs):
        self.messages.append(
            {"role": "system", "content": self.agent.initial_instruction}
        )
        super(Conversation, self).save(*args, **kwargs)


class Agent(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome", max_length=255, unique=True)
    description = models.TextField("Descrição", blank=True)
    initial_instruction = models.TextField("initial instruction")

    def __str__(self):
        return self.name
