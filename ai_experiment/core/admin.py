import pprint

from django.contrib import admin

from .models import Conversation, Agent

pp = pprint.PrettyPrinter(indent=4)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    readonly_fields = [
        'get_messages'
    ]
    list_display = (
        'created_at',
        'updated_at',
        'id',
        'user',
        'agent',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'agent')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {"fields": ("user", "agent", "mega_instance", "get_messages")}),
    )

    def get_messages(self, instance):
        return pp.pformat(instance.messages)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'updated_at',
        'id',
        'name',
        'description',
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
