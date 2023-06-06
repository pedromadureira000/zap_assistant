from django.utils import timezone
from django.db import transaction
from celery import shared_task
import sentry_sdk

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
            return "Done"
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise self.retry(exc=exc, countdown=60, max_retries=2)
    mega_api_instance = MegaAPIInstance.objects.first()
    if mega_api_instance:
        #  err_msg = "Sorry, we are having some problems with our servers. Please try again later."
        err_msg = "Desculpe, estamos tendo alguns problemas com nossos servidores. Por favor, tente novamente mais tarde."  # XXX fix it
        mega_api_instance.send_text_message(user.whatsapp, err_msg)
