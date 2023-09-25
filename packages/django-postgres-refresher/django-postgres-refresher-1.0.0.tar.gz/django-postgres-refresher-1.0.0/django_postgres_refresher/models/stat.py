__all__ = ['Stat',]

from django.db import models

class Stat(models.Model):
    schemaname = models.TextField()
    matviewname = models.TextField()
    count = models.IntegerField()
    avg_duration = models.FloatField()
    min_duration = models.FloatField()
    max_duration = models.FloatField()

    class Meta:
        ordering = ('schemaname','matviewname',)
        unique_together = [('schemaname','matviewname',)]

