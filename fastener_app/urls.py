from django.urls import path
from .views import FastenerIngestView, FastenerListView, SellerCreateView

urlpatterns = [
    path('fasteners/<int:seller_id>/', FastenerIngestView.as_view(), name='fastener-ingest'),
    path('fasteners/', FastenerListView.as_view(), name='fastener-list'),
    path('sellers', SellerCreateView.as_view(), name='seller-create'),
]
