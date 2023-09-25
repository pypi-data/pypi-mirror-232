from datetime import datetime

from django.contrib import admin
from django.utils.timesince import timesince

from ..models import Matview

class MatviewAdmin(admin.ModelAdmin):
    list_display = [
        'schemaname',
        'matviewname',
        'time',
        'timesince',
    ]
    search_fields = [
        'schemaname',
        'matviewname',
    ]

    def time(self,obj):
        return datetime.fromtimestamp(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def timesince(self,obj):
        return '%s ago' % timesince(datetime.fromtimestamp(obj.timestamp))

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Matview,MatviewAdmin)
