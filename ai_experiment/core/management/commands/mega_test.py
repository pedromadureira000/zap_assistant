from django.core.management.base import BaseCommand
from django.conf import settings
from django.shortcuts import resolve_url as r

from ai_experiment.mega_api.models import MegaAPIInstance


class Command(BaseCommand):
    help = "Test mega api"

    def handle(self, *args, **options):
        mega_test()

#  r("core:webhook")

def mega_test():
    try:
        mega_instance = MegaAPIInstance(
            instance_key=settings.MEGA_API_INSTANCE_KEY_TEST, host=settings.MEGA_API_HOST_TEST
        )
        #  response = mega_instance.get_instance()
        response = mega_instance.send_text_message("5562981243394", "Teste de envio de mensagem 2")
        #  response = mega_instance.get_webhook_data()

        #  url = settings.BASE_URL
        #  print(url)
        #  url = "https://webhook.site/40f244ed-5393-4df1-81ff-8b0effb9aab1"
        #  response = mega_instance.config_webhook(url=url, enable=True)

        #  response = mega_instance.pin_chat(to="5562981243394", option=True)

        print(' 😃 ', response)
    except Exception as e:
        print(' 😡 ', e)
