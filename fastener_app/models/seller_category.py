from django.db import models
from django.conf import settings
from fastener_app.models.seller import Seller
from fastener_app.models.fastener import Fastener


class SellerFastener(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_fasteners')
    fastener = models.ForeignKey(Fastener, on_delete=models.CASCADE, related_name='seller_fasteners')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = f'{settings.DB_SCHEMA}"."seller_fastener'
        unique_together = ('seller', 'fastener')  # Ensures a seller-fastener pair is unique

    def __str__(self):
        return f"{self.seller.name} - {self.fastener.name}"
