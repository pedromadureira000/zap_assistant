from django.contrib import admin

from .models import MegaAPIInstance


@admin.register(MegaAPIInstance)
class MegaAPIInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'instance_key', 'host', 'is_active')
    list_filter = ('is_active',)
