from rest_framework import serializers
import magic
import sentry_sdk

from ai_experiment.core.facade import get_conversation_by_instance_phone, get_user, get_user_text_input, parse_user_txt_input

from ai_experiment.core.models import Conversation
from ai_experiment.core.tasks import get_completion_and_send_to_user

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
        user = get_user(attrs['key']['remoteJid'].split('@')[0])
        mega_api_instance_phone = attrs['jid'].split(':')[0]
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
        remoteJid = validated_data['key']['remoteJid']
        phone = remoteJid.split('@')[0]
        user = get_user(phone)
        jid = validated_data['jid']
        mega_api_instance_phone = jid.split(':')[0]
        message = validated_data['message']
        try:
            conversation = validated_data['conversation']
            user_txt_input = parse_user_txt_input(
                get_user_text_input(message, conversation)
            )
            get_completion_and_send_to_user.delay(
                user.id,
                user_txt_input,
                conversation.id,
                mega_api_instance_phone
            )
            return conversation
        except Exception as err:
            sentry_sdk.capture_exception(err)
            raise err
