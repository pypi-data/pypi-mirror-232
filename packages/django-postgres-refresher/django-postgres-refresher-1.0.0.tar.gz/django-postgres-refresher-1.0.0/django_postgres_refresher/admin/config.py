from django.contrib import admin

from ..models import Config

class ConfigAdmin(admin.ModelAdmin):
    list_display = [
        'schemaname',
        'matviewname',
        'concurrently',
        'seconds',
    ]
    list_filter = [
        'schemaname',
    ]
    search_fields = [
        'schemaname',
        'matviewname'
    ]

admin.site.register(Config,ConfigAdmin)
