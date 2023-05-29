from django.core.management.base import BaseCommand
from django.conf import settings
from ai_experiment.core.facade import base64_to_file

from ai_experiment.mega_api.models import MegaAPIInstance


class Command(BaseCommand):
    help = "Test mega api"

    def handle(self, *args, **options):
        mega_test()

def mega_test():
    try:
        mega_instance = MegaAPIInstance(
            instance_key=settings.MEGA_API_INSTANCE_KEY_TEST, host=settings.MEGA_API_HOST_TEST
        )
        audio_data = {
            "mediaKey": "8XIrOzBSIQZRU/olowv6b+47yz9VfrUZj+kDA6oUlIk=",
            "directPath": "/v/t62.7117-24/28489563_940583323940629_658308074563489284_n.enc?ccb=11-4&oh=01_AdSJ5xqdt6NfQDWwBM3Noy6UmGjTb1rRNiTzI3ZRB29PoA&oe=6496EEA1",
            "url": "https://mmg.whatsapp.net/v/t62.7117-24/28489563_940583323940629_658308074563489284_n.enc?ccb=11-4&oh=01_AdSJ5xqdt6NfQDWwBM3Noy6UmGjTb1rRNiTzI3ZRB29PoA&oe=6496EEA1&mms3=true",
            "mimetype": "audio/ogg; codecs=opus",
            "messageType": "audio"
        }
        payload = {
            "messageKeys": {
                "mediaKey": audio_data["mediaKey"],
                "directPath": audio_data["directPath"],
                "url": audio_data["url"],
                "mimetype": audio_data["mimetype"],
                "messageType": "audio"
            }
        }
        response = mega_instance.download_media_message(payload)
        file_path = base64_to_file(response["data"])
        print(' 😃 ', file_path)
    except Exception as e:
        raise e
