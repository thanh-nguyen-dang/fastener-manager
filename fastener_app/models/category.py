from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = f'{settings.DB_SCHEMA}"."category'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name
