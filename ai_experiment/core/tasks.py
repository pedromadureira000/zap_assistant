import json
from random import randint

from django.utils import timezone
from django.db import transaction
from celery import shared_task
import sentry_sdk
from openai.error import RateLimitError

from ai_experiment.core.facade import add_completion_to_conversation, get_chat_completion, send_completion_to_user_with_mega_api
from ai_experiment.core.models import Conversation
from ai_experiment.mega_api.models import MegaAPIInstance
from ai_experiment.user.models import UserModel


@shared_task(bind=True)
def get_completion_and_send_to_user(self, user_id, user_txt_input, conversation_id,
                                    mega_api_instance_phone):
    now = timezone.now().isoformat()

    print(f"Running task at: {now}")

    user = UserModel.objects.get(id=user_id)
    conversation = Conversation.objects.get(id=conversation_id)
    conversation.processing_request = True
    conversation.save()

    try:
        with transaction.atomic():
            conversation.messages.append({"role": "user", "content": user_txt_input})
            completion = get_chat_completion(
                conversation.messages,
                user,
                conversation.agent.system_instruction
            )
            print('========================> completion: ',completion )
            # check if GPT wanted to call a function
            response_message = completion[0]["message"] 
            txt_completion = response_message["content"]
            audio_response = False
            if response_message.get("function_call"):
                function_name = response_message["function_call"]["name"]
                if function_name == "answer_in_audio":
                    args = json.loads(response_message["function_call"]["arguments"])
                    txt_completion = args.get("txt_completion")
                    audio_response = True
            add_completion_to_conversation(conversation, completion)
            send_completion_to_user_with_mega_api(
                user,
                mega_api_instance_phone,
                txt_completion,
                audio_response=audio_response
            )
            conversation.processing_request = False
            conversation.save()
            return "Done"
    except RateLimitError:
        conversation.processing_request = False
        conversation.save()
        err_msg_to_user = f"O servidor está sobrecarregado. Por favor, tente novamente mais tarde."
        err_msg = f"RateLimitError processing request for user {user_id} at {now}"
        mega_api_instance = MegaAPIInstance.objects.first()
        mega_api_instance.send_text_message("556293378753", err_msg)
        mega_api_instance.send_text_message(user.whatsapp, err_msg_to_user)
        raise RateLimitError
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        if (self.request.retries >= 2):
            conversation.processing_request = False
            conversation.save()
            return "Didn't work 😢"
        countdown = randint(5, 15)
        raise self.retry(exc=exc, countdown=countdown, max_retries=2)
    finally:
        # This will run 3 times if reach max_retries
        pass
