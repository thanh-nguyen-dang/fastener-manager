from django.db import models
from django.conf import settings
from fastener_app.models.category import Category
from fastener_app.models.thread_size import ThreadSize
from fastener_app.models.material import Material
from fastener_app.models.finish import Finish

class Fastener(models.Model):
    product_id = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    thread_size = models.ForeignKey(ThreadSize, on_delete=models.CASCADE, related_name='fasteners')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='fasteners')
    finish = models.ForeignKey(Finish, on_delete=models.CASCADE, related_name='fasteners')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fasteners')

    def __str__(self):
        return f"{self.product_id} - {self.description}"

    class Meta:
        db_table = f'{settings.DB_SCHEMA}"."fastener'
        indexes = [
            models.Index(name="fastener_name", fields=['description']),
            models.Index(name="features", fields=['thread_size', 'material', 'finish', 'category'])
        ]
