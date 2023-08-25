from rest_framework import serializers
import magic
import sentry_sdk

from ai_experiment.core.facade import format_phone_for_mega_api, get_conversation_by_instance_phone, get_instance_phone_from_jid, get_user_or_none_by_phone, get_user_text_input, parse_user_txt_input

from ai_experiment.core.models import Conversation
from ai_experiment.core.tasks import get_completion_and_send_to_user
from ai_experiment.mega_api.models import MegaAPIInstance


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        # Check if the file is an MP3
        mime_type = magic.from_buffer(value.read(1024), mime=True)
        if mime_type != 'audio/mpeg':
            raise serializers.ValidationError("The file must be a valid MP3.")
        return value


class MessagesSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()

    def validate_role(self, value):
        if value not in ['user', 'assistant', 'system']:
            raise serializers.ValidationError("The role must be either 'user', 'assistant', or 'system'.")
        return value

    def validate_content(self, value):
        if not value:
            raise serializers.ValidationError("The content must not be empty.")
        return value


class ChatCompletionSerializer(serializers.Serializer):
    messages = MessagesSerializer(many=True)
    system_instruction = serializers.CharField()


class ConversationalAgentSerializer(serializers.Serializer):
    user_input = serializers.CharField()
    agent = serializers.CharField()

    def validate_agent(self, value):
        from ai_experiment.core.models import Agent
        try:
            agent = Agent.objects.get(name=value)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("The agent does not exist.")
        return agent


class WebhookConversationSerializer(serializers.Serializer):
    instance_key = serializers.CharField()
    jid = serializers.CharField()
    messageType = serializers.ChoiceField(
        choices=['conversation', 'extendedTextMessage', 'audioMessage']
    )
    key = serializers.DictField()
    pushName = serializers.CharField()
    broadcast = serializers.BooleanField()
    message = serializers.DictField()

    def validate_key(self, value):
        if value.get("fromMe") is True:
            raise serializers.ValidationError(
                "We don't process actions from the bot."
                "Only messages from the user."
            )
        return value

    def validate(self, attrs):
        phone = attrs['key']['remoteJid'].split('@')[0]
        user = get_user_or_none_by_phone(phone)
        if not user:
            mega_api_instance = MegaAPIInstance.objects.first()
            # TODO all send_text_message should be done by celery ( add a facade to send txt msgs )
            err_msg_to_user = f"Você não tem permissão para acessar esse serviço. Por favor peça ao administrador para registrar sua conta."
            mega_api_instance.send_text_message(format_phone_for_mega_api(phone), err_msg_to_user)
            raise serializers.ValidationError("User not found by phone.")

        mega_api_instance_phone = get_instance_phone_from_jid(attrs['jid'])

        try:
            conversation = get_conversation_by_instance_phone(
                user, 
                mega_api_instance_phone
            )
        except Conversation.DoesNotExist:
            sentry_sdk.capture_message(
                f"Phone number {user.whatsapp} has tried to send a message"
                f" to {mega_api_instance_phone} without a conversation."
            )
            raise serializers.ValidationError("Conversation does not exist.")
        attrs['conversation'] = conversation
        return attrs

    def create(self, validated_data):
        phone = validated_data['key']['remoteJid'].split('@')[0]
        user = get_user_or_none_by_phone(phone)
        mega_api_instance_phone = get_instance_phone_from_jid(validated_data['jid'])
        message = validated_data['message']
        try:
            conversation = validated_data['conversation']
            user_txt_input = parse_user_txt_input(
                get_user_text_input(message, conversation)
            )
            if conversation.processing_request:
                #  err_msg = "Sorry, we are still processing your previous request. Please wait a few seconds and try again."
                err_msg = "Desculpe, ainda estamos processando sua solicitação anterior. Por favor, aguarde alguns segundos e tente novamente."
                mega_api_instance = MegaAPIInstance.objects.first()
                if mega_api_instance:
                    mega_api_instance.send_text_message(user.whatsapp, err_msg)
            else:
                get_completion_and_send_to_user.delay(
                    user.id,
                    user_txt_input,
                    conversation.id,
                    mega_api_instance_phone
                )
            return conversation
        except Exception as err:
            sentry_sdk.capture_exception(err)
            try:
                mega_api_instance = MegaAPIInstance.objects.first()
                if mega_api_instance:
                    #  err_msg = "Sorry, we are having some problems with our servers. Please try again later."
                    err_msg = "Desculpe, estamos tendo alguns problemas com nossos servidores. Por favor, tente novamente mais tarde."  # XXX fix it
                    mega_api_instance.send_text_message(user.whatsapp, err_msg)
            except Exception:
                pass
            raise err
