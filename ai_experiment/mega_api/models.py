import logging
import requests

from django.db import models


log = logging.getLogger("mega")


class MegaAPIException(Exception):
    pass


class MegaAPI:
    def __init__(self, instance_key, host):
        self._instance_key = instance_key
        self._host = host

    @property
    def instance_key(self):
        return self._instance_key

    @property
    def authorization_token(self):
        return self.instance_key.split('megastart-')[1]

    @property
    def host(self):
        return self._host

    def get_base_url(self):
        return f"https://{self.host}/rest"

    def get_url(self, endpoint):
        endpoint_formated = endpoint.format(instance_key=self.instance_key)
        return f"{self.get_base_url()}/{endpoint_formated}"

    def request(self, endpoint, method="GET", **kwargs):
        log.debug(
            f"Requesting endpoint '{endpoint}' to MegaAPI"
            f" (instance: {self.instance_key})..."
        )

        headers = {
            'Authorization': f'Bearer {self.authorization_token}',
            'Content-Type': 'application/json'
        }
        response = requests.request(
            method, self.get_url(endpoint), headers=headers, **kwargs
        ).json()

        #  if "error" in response:
            #  message = response["error"]
            #  if "You are already connected" not in message:
                #  log.error(message)
                #  raise MegaAPIException(message)

        return response


class MegaAPIInstance(models.Model):
    class Meta:
        verbose_name = "instância"
        verbose_name_plural = "instâncias"
        ordering = ("-id",)

    instance_key = models.CharField(max_length=50, unique=True)
    host = models.CharField(max_length=255, default="apistart01.megaapi.com.br")
    phone = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField("ativo?", default=True)

    def __str__(self):
        return self.instance_key

    def _get_mega_instance(self):
        return MegaAPI(instance_key=self.instance_key, host=self.host)

    def get_instance(self):
        mega = self._get_mega_instance()
        return mega.request(
            "instance/{instance_key}"
        )

    def send_text_message(self, phone, message):
        mega = self._get_mega_instance()
        #  Note that while sending to single chat, the id should not contain @s.whatsapp.net.
        #  However, while sending to groups, the id should end with @g.us
        payload = {
            "messageData": {
                "to": phone,
                "text": message,
            }
        }
        return mega.request(
            "sendMessage/{instance_key}/text", method="POST", json=payload
            #  "sendMessage/{instance_key}/text", method="POST", data=json.dumps(payload) XXX Also works
        )

    def pin_chat(self, to, option=True):
        mega = self._get_mega_instance()
        payload = {
            "to": to + "@s.whatsapp.net",
            "option": option
        }
        return mega.request(
            "chat/{instance_key}/pinChat", method="POST", json=payload
        )

    def get_webhook_data(self):
        mega = self._get_mega_instance()
        return mega.request(
            "webhook/{instance_key}"
            #  "webhook/{instance_key}/configWebhook"
        )

    def config_webhook(self, url, enable):
        mega = self._get_mega_instance()
        payload = {
            "messageData": {
                "webhookUrl": url,
                "webhookEnabled": enable
            }
        }
        return mega.request(
            "webhook/{instance_key}/configWebhook", method="POST", json=payload
        )

    def download_media_message(self, payload):
        mega = self._get_mega_instance()
        return mega.request(
            "instance/downloadMediaMessage/{instance_key}", method="POST", json=payload
        )
