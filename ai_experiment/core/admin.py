from django.contrib import admin

from .models import Conversation, Agent


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'updated_at',
        'id',
        'user',
        'agent',
        'messages',
    )
    list_filter = ('created_at', 'updated_at', 'user', 'agent')
    date_hierarchy = 'created_at'


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'updated_at',
        'id',
        'name',
        'description',
        'initial_instruction',
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
