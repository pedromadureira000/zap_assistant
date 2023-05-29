import os
from datetime import datetime

import whisper
import openai
from django.conf import settings
from django.contrib.auth import get_user_model

from ai_experiment.core.models import Conversation
from ai_experiment.mega_api.models import MegaAPIInstance
#  import sentry_sdk


def invalid_day_of_month(day_of_month):
    if type(day_of_month) == int:
        is_invalid = day_of_month not in range(1, 32)
    else:
        is_invalid = (type(day_of_month) != str or not day_of_month.isdigit()) \
                or (int(day_of_month) not in range(1, 32))
    return is_invalid


# XXX what does `fp32 used instead` mean?
def get_transcription(in_memory_file):
    time_now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    temporary_audio_folder = "/tmp/temp_transcription_audio"
    temporary_file_path = temporary_audio_folder + f'/{time_now}.mp3'
    if not os.path.exists(temporary_audio_folder):
        os.makedirs(temporary_audio_folder)
    with open(temporary_file_path, 'wb') as temp_file:
        for chunk in in_memory_file.chunks():
            temp_file.write(chunk)
    if settings.LOCAL_TRANSCRIPTION:
        model = whisper.load_model("small")
        result = model.transcribe(temporary_file_path)
        return result["text"]
    audio_file= open(temporary_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


def get_chat_completion(messages, user):
    messages_payload = [
        {"role": ord_dict["role"], "content": ord_dict["content"]} for ord_dict in messages
    ]

    openai.api_key = settings.OPENAI_API_KEY
    completion = openai.ChatCompletion.create(
        user=str(user.id),
        model="gpt-3.5-turbo",
        messages=messages_payload,
    )
    return completion.choices


def get_or_create_conversation_by_agent(user, agent):
    conversation, created = Conversation.objects.get_or_create(
        user=user,
        agent=agent,
        mega_instance__instance_key=settings.MEGA_API_INSTANCE_KEY_TEST
    )
    if created:
        conversation.messages.append(
            {"role": "system", "content": agent.initial_instruction}
        )
    return conversation


def get_conversation_by_instance_phone(user, instance_phone):
    conversation = Conversation.objects. \
            get(user=user, mega_instance__phone=instance_phone)
    return conversation
    

def add_completion_to_conversation(conversation, completion):
    conversation.messages.append(completion[0]["message"])
    conversation.save()
    return conversation


def get_user(phone):
    user_model = get_user_model()
    return user_model.objects.filter(whatsapp=phone).first()


def get_user_text_input(message, conversation):
    if message.get("conversation"):
        return message["conversation"]
    elif message.get("extendedTextMessage"):
        return message["extendedTextMessage"]["text"]
    elif message.get("audioMessage"):
        audio_data = message.get("audioMessage")
        payload = {
            "messageKeys": {
                "mediaKey": audio_data["mediaKey"],
                "directPath": audio_data["directPath"],
                "url": audio_data["url"],
                "mimetype": audio_data["mimetype"],
                "messageType": "audio"
            }
        }
        mega_instance = conversation.mega_instance
        response = mega_instance.download_media_message(payload)
        audio_base64 = response["data"]
        audio_file = base64_to_file(audio_base64)
        transcription = get_transcription(audio_file)
        return transcription


def base64_to_file(base64_to_file):
    pass

