import base64
from django.core.management.base import BaseCommand
from django.conf import settings
from elevenlabs import generate

from ai_experiment.mega_api.models import MegaAPIInstance


class Command(BaseCommand):
    help = "Test elevenlabs"

    def handle(self, *args, **options):
        elevenlabs_test()

def elevenlabs_test():
    try:
        audio = generate(
            text='Oi, tudo bem contigo?',
            voice="Liam",
            model='eleven_multilingual_v2'
        )
        base64_bytes = base64.b64encode(audio)
        base64_str = base64_bytes.decode('ascii')
        base64audioDataURI = f"data:audio/mp3;base64,{base64_str}"

        mega_instance = MegaAPIInstance(
            instance_key=settings.MEGA_API_INSTANCE_KEY_TEST, host=settings.MEGA_API_HOST_TEST
        )
        response = mega_instance.send_audio("556293378753", base64audioDataURI)
        print(' 😃 ', response)
    except Exception as e:
        raise e
