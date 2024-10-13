from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import re

import fastener_app.models.constants as constants



class ThreadSize(models.Model):
    name = models.CharField(max_length=100)  # e.g., "M12" for description purposes
    thread_type = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.value) for tag in constants.ThreadType]
    )
    unit = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.value) for tag in constants.UnitType]
    )
    metric_size_str = models.CharField(max_length=50, blank=True, null=True)  # e.g., "M12-1.75"
    metric_size_num = models.FloatField(blank=True, null=True)  # e.g., 12.0
    imperial_size_str = models.CharField(max_length=50, blank=True, null=True)  # e.g., "1/2-13"
    imperial_size_num = models.FloatField(blank=True, null=True)  # e.g., 0.5
    thread_per_unit = models.FloatField()  # Threads per unit (TPI or TPM)

    def validate(self):
        """
        Custom validation to ensure data integrity for ThreadSize model.
        """
        # Ensure that if metric_size_str is provided, it follows the correct format (e.g., "M12-1.75")
        if self.metric_size_str and not re.match(constants.METRIC_REG, self.metric_size_str):
            raise ValidationError(
                f"Value {self.metric_size_str} is not a valid metric_size_str format. Expected format: 'M12-1.75'."
            )

        # Ensure that if imperial_size_str is provided, it follows the correct format (e.g., "1/2-13")
        if self.imperial_size_str and not re.match(constants.IMPERIAL_REG, self.imperial_size_str):
            raise ValidationError(
                f"Value {self.imperial_size_str} is not a valid imperial_size_str format. Expected format: '1/2-13'."
            )

        # Ensure that metric_size_num and imperial_size_num are positive numbers if they are provided
        if self.metric_size_num is not None and self.metric_size_num <= 0:
            raise ValidationError(f"Metric size must be a positive number. But receive {self.metric_size_num}.")

        if self.imperial_size_num is not None and self.imperial_size_num <= 0:
            raise ValidationError(f"Imperial size must be a positive number. But receive {self.imperial_size_num}.")

        # Ensure that thread_per_unit is a positive number (either TPM or TPI)
        if self.thread_per_unit <= 0:
            raise ValidationError(
                f"Thread per unit (TPM or TPI) must be a positive number. Received {self.thread_per_unit}"
            )

    def save(self, *args, **kwargs):
        # Ensure the clean method is called before saving the model
        self.validate()
        super().save(*args, **kwargs)

    class Meta:
        db_table = f'{settings.DB_SCHEMA}"."thread_size'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name
