__all__ = ['Config',]

from django.db import models

class Config(models.Model):
    schemaname = models.CharField(max_length=255)
    matviewname = models.CharField(max_length=255)
    concurrently = models.BooleanField()
    seconds = models.IntegerField()

    class Meta:
        db_table = 'postgres_refresher_config'
        ordering = ('schemaname','matviewname',)
        unique_together = [('schemaname', 'matviewname',)]
