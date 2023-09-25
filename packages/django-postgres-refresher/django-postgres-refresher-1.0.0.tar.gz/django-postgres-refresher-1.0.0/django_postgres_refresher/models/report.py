__all__ = ['Report',]

from django.db import models

class Report(models.Model):
    schemaname = models.TextField()
    matviewname = models.TextField()
    duration = models.FloatField()
    timestamp = models.IntegerField()

    class Meta:
        db_table = 'postgres_refresher_report'
        ordering = ('-timestamp',)

