import os
from datetime import datetime
import re
import base64
import io
import wave
import sentry_sdk

import whisper
import openai
from django.conf import settings
from django.contrib.auth import get_user_model
from pydub import AudioSegment

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
def get_transcription_with_in_memory_file(in_memory_file):
    time_now = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    temporary_audio_folder = "/tmp/temp_transcription_audio"
    temporary_file_path = temporary_audio_folder + f'/{time_now}.mp3'
    if not os.path.exists(temporary_audio_folder):
        os.makedirs(temporary_audio_folder)
    with open(temporary_file_path, 'wb') as temp_file:
        for chunk in in_memory_file.chunks():
            temp_file.write(chunk)
    return get_transcription_with_file_path(temporary_file_path)


def get_transcription_with_file_path(temporary_file_path):
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
        max_tokens=922
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


def get_user(phone):
    user_model = get_user_model()
    return user_model.objects.filter(whatsapp=phone).first()


def parse_txt_input(txt_input):
    if len(txt_input) > 4469:
        sentry_sdk.capture_message(
            f"Input text is too long: {len(txt_input)} characters"
        )
        return txt_input[:4469] + "..."
    return txt_input


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
        audio_file_path = base64_to_file(audio_base64)
        transcription = get_transcription_with_file_path(audio_file_path)
        return transcription


def sanitize_base64_string(base64_data):
    # Remove white spaces, line breaks, and any prefix/suffix
    sanitized_data = re.sub(r"\s+|data:audio/.*?;base64,", "", base64_data)
    return sanitized_data


def base64_to_file(base64_data):
    audio_data = base64.b64decode(sanitize_base64_string(base64_data))
    audio_file = io.BytesIO(audio_data)
    audio_segment = AudioSegment.from_file(audio_file, format='ogg')
    file_name = "/tmp/temp_transcription_audio" + \
            datetime.now().strftime('%Y-%m-%d-%H%M%S')
    output_file = f'{file_name}.mp3'  # Replace with the desired output file name
    audio_segment.export(output_file, format='mp3')
    print(f"Audio file '{output_file}' has been created.")
    return output_file


def send_completion_to_user(user, mega_api_instance_phone, completion):
    mega_api_instance = MegaAPIInstance.objects.get(phone=mega_api_instance_phone)
    mega_api_instance.send_text_message(user.whatsapp, completion)
