__all__ = ['Rule',]

from django.db import models

class Rule(models.Model):
    oid = models.IntegerField(primary_key=True)
    schemaname = models.CharField(max_length=255)
    tablename = models.CharField(max_length=255)
    rulename = models.CharField(max_length=255)
    event = models.CharField(max_length=255)
    definition = models.CharField(max_length=255)

    class Meta:
        db_table = 'django_postgres_rule'
        ordering = ('schemaname','tablename','rulename',)

