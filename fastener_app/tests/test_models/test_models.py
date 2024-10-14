# fastener_app/tests/test_models.py

import pytest
from django.db import IntegrityError
from fastener_app.models import (
    Seller,
    ThreadSize,
    Material,
    Finish,
    Category,
    Fastener,
    SellerFastener
)

@pytest.mark.django_db
def test_seller_creation(seller):
    assert seller.name.startswith('Seller')
    assert '@' in seller.contact_email
    assert seller.csv_mapping == {
        'id': 'product_id',
        'name': 'description',
        'size_and_length': 'thread_size',
        'material': 'material',
        'surface_treatment': 'finish',
        'category': 'category',
        'price': 'price',
        'quantity': 'quantity'
    }

@pytest.mark.django_db
def test_thread_size_creation(thread_size):
    assert thread_size.name.startswith('M')
    assert thread_size.thread_type in ['METRIC', 'IMPERIAL']
    assert thread_size.unit in ['MILLIMETER', 'INCH']

@pytest.mark.django_db
def test_material_creation(material):
    assert material.name.startswith('Material')

@pytest.mark.django_db
def test_finish_creation(finish):
    assert finish.name.startswith('Finish')

@pytest.mark.django_db
def test_category_creation(category):
    assert category.name.startswith('Category')

@pytest.mark.django_db
def test_fastener_creation(fastener):
    assert fastener.product_id.startswith('F')
    assert len(fastener.description) > 0
    assert fastener.thread_size.name.startswith('M')
    assert fastener.material.name.startswith('Material')
    assert fastener.finish.name.startswith('Finish')
    assert fastener.category.name.startswith('Category')

@pytest.mark.django_db
def test_seller_fastener_creation(seller_fastener):
    assert seller_fastener.seller.name.startswith('Seller')
    assert seller_fastener.fastener.product_id.startswith('F')
    assert seller_fastener.price >= 0
    assert seller_fastener.quantity >= 0
