from celery import shared_task
from django.conf import settings
from django.shortcuts import resolve_url as r
from django.utils import timezone
import sentry_sdk

from ai_experiment.zapi.models import ZApiInstance


#  @shared_task(bind=True)
#  def send_checkin_link(self, phone_number, link_id):
    #  now = timezone.now().isoformat()

    #  try:
        #  zapi_instance = ZApiInstance(
            #  instance_id=settings.ZAPI_INSTANCE_ID, token=settings.ZAPI_TOKEN
        #  )
        #  link = settings.BASE_URL + r("core:answer_form_template", link_id=link_id)
        #  msg = settings.CHECKIN_LINK_MESSAGE + link
        #  if phone_number[:2] != "55":
            #  sentry_sdk.capture_message(
                #  f"Phone number {phone_number} has the wrong format. Not sending link to client."
            #  )
        #  else:
            #  print(f'--- [{now}] Sending message "{msg}" to phone {phone_number}.')
            #  zapi_instance.send_link_message(msg, phone_number, link)

    #  except Exception as exc:
        #  print(f"Error sending message to {phone_number}: {exc}")
        #  raise self.retry(exc=exc, countdown=60, max_retries=5)
    #  return "Done"
