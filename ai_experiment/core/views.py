from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.shortcuts import render
from rest_framework import status, permissions
from ai_experiment.core.constants import WEBHOOK_SERIALIZERS

from ai_experiment.core.facade import start_trial


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def home(request):
    language = 'pt' if 'pt-BR' in request.META.get('HTTP_ACCEPT_LANGUAGE', 'en-US') else 'en'
    if request.method == 'POST':
        phone_number = request.POST.get("phone")
        user_name = request.POST.get("name")
        try:
            start_trial(user_name, phone_number)
        except Exception as er:
            print(er)
            error_msg =  "Algo deu errado. Tente novamente mais tarde" if language == 'pt' \
                    else "Something went wrong. Try again later"
            if "Number not registered on WhatsApp" in str(er):
                error_msg = "Número não cadastrado no WhatsApp" if language == 'pt' else "Number not registered on WhatsApp"
            return render(request, "home.html", {"error": error_msg, "lang": language})
        return render(request, "trial_success.html", {'lang': language})
    return render(request, "home.html", {"lang": language})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trial_success(request):
    language = 'pt' if 'pt-BR' in request.META.get('HTTP_ACCEPT_LANGUAGE', 'en-US') else 'en'
    return render(request, "trial_success.html", {'lang': language})


@api_view(['POST', 'GET'])
@permission_classes([permissions.AllowAny])
def webhook(request, webhook_id):
    if str(webhook_id) != settings.WEBHOOK_ID:
        return Response({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        message_type = request.data.get('messageType')
        if WEBHOOK_SERIALIZERS.get(message_type):
            serializer = WEBHOOK_SERIALIZERS[message_type](data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'ok'})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'not supported'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        return Response({'status': 'ok'})
    else:
        return Response({'error': 'method not supported'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
