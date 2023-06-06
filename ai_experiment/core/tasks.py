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
                conversation.system_instruction
            )
            print('========================> completion: ',completion )
            add_completion_to_conversation(conversation, completion)
            send_completion_to_user_with_mega_api(
                user,
                mega_api_instance_phone,
                completion
            )
            conversation.processing_request = False
            conversation.save()
            return "Done"
    except RateLimitError:
        err_msg_to_user = f"O servidor está sobrecarregado. Por favor, tente novamente mais tarde."
        err_msg = f"RateLimitError processing request for user {user_id} at {now}"
        mega_api_instance = MegaAPIInstance.objects.first()
        mega_api_instance.send_text_message("556293378753", err_msg)
        mega_api_instance.send_text_message(user.whatsapp, err_msg_to_user)
        #  XXX block it somehow. Like with a flag
        raise RateLimitError
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        countdown = randint(5, 15)
        raise self.retry(exc=exc, countdown=countdown, max_retries=2)

    conversation.processing_request = False
    conversation.save()

    err_msg = f"Error processing request for user {user_id} at {now}"
    err_msg_to_user = f"Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde."
    mega_api_instance = MegaAPIInstance.objects.first()
    mega_api_instance.send_text_message("556293378753", err_msg)
    mega_api_instance.send_text_message(user.whatsapp, err_msg_to_user)
