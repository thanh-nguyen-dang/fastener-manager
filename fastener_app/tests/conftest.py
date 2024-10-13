import pytest
from rest_framework.test import APIClient
from fastener_app.tests.factories import (
    SellerFactory,
    FastenerFactory,
    SellerFastenerFactory,
    ThreadSizeFactory,
    MaterialFactory,
    FinishFactory,
    CategoryFactory
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def seller():
    return SellerFactory()

@pytest.fixture
def thread_size():
    return ThreadSizeFactory()

@pytest.fixture
def material():
    return MaterialFactory()

@pytest.fixture
def finish():
    return FinishFactory()

@pytest.fixture
def category():
    return CategoryFactory()

@pytest.fixture
def fastener(thread_size, material, finish, category):
    return FastenerFactory(
        thread_size=thread_size,
        material=material,
        finish=finish,
        category=category
    )

@pytest.fixture
def seller_fastener(seller, fastener):
    return SellerFastenerFactory(
        seller=seller,
        fastener=fastener
    )
