import pprint

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.shortcuts import render
from rest_framework import status, permissions
from ai_experiment.core.constants import WEBHOOK_SERIALIZERS

from ai_experiment.core.facade import add_completion_to_conversation, get_chat_completion, get_or_create_conversation_by_agent, get_transcription_with_in_memory_file, start_trial
from ai_experiment.core.serializers import ConversationalAgentSerializer, FileUploadSerializer, ChatCompletionSerializer


pp = pprint.PrettyPrinter(indent=4)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def home(request):
    language = 'pt' if 'pt-BR' in request.META.get('HTTP_ACCEPT_LANGUAGE') else 'en'
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
        return render(request, "trial_success.html", {'phone_number': phone_number, 'lang': language})
    return render(request, "home.html", {"lang": language})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trial_success(request):
    return render(request, "trial_success.html")


@api_view(['POST'])
def audio_transcription(request):
    if not request.user.is_superuser:
        return Response({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        transcription = get_transcription_with_in_memory_file(uploaded_file)
        return Response({'transcription': transcription})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def chat_completion(request):
    if not request.user.is_superuser:
        return Response({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = ChatCompletionSerializer(data=request.data)
    if serializer.is_valid():
        messages = serializer.validated_data['messages']
        system_instruction = serializer.validated_data['system_instruction']
        try:
            completion = get_chat_completion(messages, request.user, system_instruction)
            return Response({'completion': completion})
        except Exception as er:
            err_msg = str(er) if settings.DEBUG else 'something went wrong'
            return Response({'error': err_msg}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def conversational_agent(request, agent):
    if not request.user.is_superuser:
        return Response({'error': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        serializer = ConversationalAgentSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']
            try:
                conversation = get_or_create_conversation_by_agent(request.user, agent)
                conversation.messages.append({"role": "user", "content": user_input})
                conversation.save()
                completion = get_chat_completion(conversation.messages, request.user)
                pp.pprint(conversation.messages)
                pp.pprint(completion)
                add_completion_to_conversation(conversation, completion)
                return Response({'completion': completion[0]["message"]["content"]})
            except Exception as er:
                err_msg = str(er) if settings.DEBUG else 'something went wrong'
                return Response({'error': err_msg}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        conversation = request.user.conversations.filter(agent__name=agent).first()
        messages = conversation.messages if conversation else []
        if not request.user.is_superuser:
            messages = messages[1:]
        return Response({'messages': messages if messages else []})
    else:
        return Response({'error': 'method not supported'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
