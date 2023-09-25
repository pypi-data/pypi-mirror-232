from datetime import datetime

from django.contrib import admin
from django.db.models import Count, Max, Min, Avg

from ..models import Report, Stat

class StatAdmin(admin.ModelAdmin):
    list_display = [
        'schemaname',
        'matviewname',
        'count',
        'avg_duration',
        'min_duration',
        'max_duration',
    ]
    search_fields = [
        'schemaname',
        'matviewname',
    ]

    def get_queryset(self, request):
        r_list = list(Report.objects.values('schemaname','matviewname').annotate(
            count=Count('duration'),
            avg_duration=Avg('duration'),
            min_duration=Min('duration'),
            max_duration=Max('duration')
        ))
        stat_list = list(Stat.objects.all())
        for s in stat_list:
            r = next(filter(
                lambda r:r['schemaname']==s.schemaname and r['matviewname']==s.matviewname,
                r_list
            ),None)
            if not r:
                Stat.objects.filter(id=stat.id).delete()
        stat_create_list = []
        for r in r_list:
            schemaname=r['schemaname']
            matviewname=r['matviewname']
            count=r['count']
            avg_duration=round(r['avg_duration'],3)
            min_duration=round(r['min_duration'],3)
            max_duration=round(r['max_duration'],3)
            stat = next(filter(
                lambda s:s.schemaname==schemaname and s.matviewname==matviewname,
                stat_list
            ),None)
            if not stat or stat.count!=count:
                stat_create_list+=[Stat(
                    schemaname=schemaname,
                    matviewname=matviewname,
                    count=count,
                    avg_duration=avg_duration,
                    min_duration=min_duration,
                    max_duration=max_duration
                )]
        Stat.objects.bulk_create(stat_create_list,            update_conflicts=True,
            unique_fields = ['schemaname','matviewname'],
            update_fields = ['count','avg_duration','min_duration','max_duration']
        )
        return super().get_queryset(request)

    def count(self,obj):
        return obj.count
    count.short_description = "count"

    def avg_duration(self,obj):
        return round(obj.avg_duration,3)

    def min_duration(self,obj):
        return round(obj.min_duration,3)

    def max_duration(self,obj):
        return round(obj.max_duration,3)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Stat,StatAdmin)
