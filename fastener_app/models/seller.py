from django.db import models
from django.conf import settings


class Seller(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    csv_mapping = models.JSONField(default=dict, blank=True, null=True)  # Stores CSV column mappings

    class Meta:
        db_table = f'{settings.DB_SCHEMA}"."seller'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name
