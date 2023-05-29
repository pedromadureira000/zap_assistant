from django.db.models.signals import pre_save
from django.dispatch import receiver


#  @receiver(pre_save, sender=CheckInAnswer)
#  def answer_post_save(sender, instance, **kwargs):
    #  if instance.pk:
        #  previous_answer = CheckInAnswer.objects.get(pk=instance.pk)
        #  if instance.status == 'answered' and previous_answer.status == 'pending':
            #  professional_whatsapp = instance.form.created_by.whatsapp
            #  if professional_whatsapp:
                #  notify_professional.delay(instance.id, professional_whatsapp)
