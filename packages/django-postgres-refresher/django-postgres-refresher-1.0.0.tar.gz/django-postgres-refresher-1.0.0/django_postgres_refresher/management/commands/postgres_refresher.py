import time

from django.core.management.base import BaseCommand

from ...models import Config, Matview, Report
from .utils import execute_sql

CONFIG_LIST = list(Config.objects.all())

class Command(BaseCommand):

    def handle(self,*args,**options):
        create_matview_list = []
        create_report_list = []
        matview_list = list(Matview.objects.all())
        for config in CONFIG_LIST:
            schemaname = config.schemaname
            matviewname = config.matviewname
            seconds = config.seconds
            matview = next(filter(
                lambda m:m.schemaname==schemaname and m.matviewname==matviewname,
                matview_list
            ),None)
            if not matview or matview.timestamp+seconds<int(time.time()):
                c = 'CONCURRENTLY ' if config.concurrently else ''
                sql = 'REFRESH MATERIALIZED VIEW %s"%s"."%s";' % (c,schemaname,matviewname)
                timestamp = time.time()
                execute_sql(sql)
                create_matview_list+=[Matview(
                    schemaname=schemaname,
                    matviewname=matviewname,
                    timestamp=int(timestamp)
                )]
                create_report_list+=[Report(
                    schemaname=schemaname,
                    matviewname=matviewname,
                    duration=time.time()-timestamp,
                    timestamp=int(timestamp)
                )]
        # todo: transaction
        Matview.objects.bulk_create(create_report_list,
            update_conflicts=True,
            unique_fields = ['schemaname','matviewname'],
            update_fields = ['timestamp']
        )
        Report.objects.bulk_create(create_report_list)
