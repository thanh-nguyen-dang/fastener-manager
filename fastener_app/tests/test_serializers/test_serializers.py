import pytest
from rest_framework.exceptions import ValidationError
from fastener_app.serializers import (
    ThreadSizeSerializer, MaterialSerializer, FinishSerializer, CategorySerializer,
    SellerSerializer, FastenerSerializer, SellerFastenerSerializer
)
from fastener_app.models import Seller, Fastener, ThreadSize, Material, Finish, Category, SellerFastener
from django.utils.timezone import now

from fastener_app.tests.conftest import thread_size


@pytest.mark.django_db
class TestThreadSizeSerializer:

    def test_valid_thread_size(self):
        """Test that a valid ThreadSize object serializes correctly."""
        thread_size = ThreadSize.objects.create(
            name="M12",
            thread_type="metric",
            unit="millimeter",
            metric_size_str="M12-1.75",
            metric_size_num=12.0,
            imperial_size_str="1/2-13",
            imperial_size_num=0.5,
            thread_per_unit=13.0
        )
        serializer = ThreadSizeSerializer(instance=thread_size)
        assert serializer.data['name'] == "M12"
        assert serializer.data['metric_size_num'] == 12.0

    def test_invalid_metric_size_num(self):
        """Test that an invalid metric_size_num raises a ValidationError."""
        data = {
            'name': 'M12',
            'thread_type': 'metric',
            'unit': 'millimeter',
            'metric_size_num': -12.0,  # Invalid negative number
        }
        serializer = ThreadSizeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'metric_size_num' in serializer.errors
        assert serializer.errors['metric_size_num'][0] == "Metric size must be a positive number."

    def test_invalid_imperial_size_num(self):
        """Test that an invalid imperial_size_num raises a ValidationError."""
        data = {
            'name': '1/2-13',
            'thread_type': 'imperial',
            'unit': 'inch',
            'imperial_size_num': -0.5,  # Invalid negative number
        }
        serializer = ThreadSizeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'imperial_size_num' in serializer.errors
        assert serializer.errors['imperial_size_num'][0] == "Imperial size must be a positive number."


@pytest.mark.django_db
class TestSellerSerializer:

    def test_valid_seller(self):
        """Test that a valid Seller object serializes correctly."""
        seller = Seller.objects.create(
            name="Seller A",
            contact_email="sellerA@example.com",
            phone_number="+1234567890",
            address="123 Seller Street",
            csv_mapping={'csv_field_1': 'product_id', 'csv_field_2': 'description'}
        )
        serializer = SellerSerializer(instance=seller)
        assert serializer.data['name'] == "Seller A"
        assert serializer.data['contact_email'] == "sellerA@example.com"

    def test_invalid_csv_mapping(self):
        """Test that invalid csv_mapping raises a ValidationError."""
        seller = Seller(
            name="Seller B",
            contact_email="sellerB@example.com",
            phone_number="+1234567890",
            address="456 Seller Avenue",
            csv_mapping={'csv_field_1': 'description'}  # Missing required fields
        )
        serializer = SellerSerializer(instance=seller)
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_csv_mapping(seller.csv_mapping)
        assert "Missing required fields in csv_mapping" in str(excinfo.value)

    def test_get_required_fastener_fields(self):
        """Test that required fields from Fastener model are fetched correctly."""
        serializer = SellerSerializer()
        required_fields = serializer.get_required_fastener_fields()
        assert 'product_id' in required_fields
        assert 'description' in required_fields


@pytest.mark.django_db
class TestSellerFastenerSerializer:

    def test_valid_seller_fastener(self):
        """Test that a valid SellerFastener object serializes correctly."""
        seller = Seller.objects.create(
            name="Seller A",
            contact_email="sellerA@example.com",
            phone_number="+1234567890",
            address="123 Seller Street",
            csv_mapping={'csv_field_1': 'product_id', 'csv_field_2': 'description'}
        )
        thread_size = ThreadSize.objects.create(name="M12", thread_type="metric", unit="millimeter", thread_per_unit=13)
        material = Material.objects.create(name="Steel")
        finish = Finish.objects.create(name="Galvanized")
        category = Category.objects.create(name="Hex Cap Screw")
        fastener = Fastener.objects.create(
            product_id="F001",
            description="M12 Hex Cap Screw",
            thread_size=thread_size,
            material=material,
            finish=finish,
            category=category
        )
        seller_fastener = SellerFastener.objects.create(
            seller=seller,
            fastener=fastener,
            price=10.99,
            quantity=100,
            last_updated=now()
        )
        serializer = SellerFastenerSerializer(instance=seller_fastener)
        assert serializer.data['price'] == str(10.99)
        assert serializer.data['quantity'] == 100
        assert serializer.data['seller']['name'] == "Seller A"
        assert serializer.data['fastener']['product_id'] == "F001"

    def test_invalid_seller_fastener(self):
        """Test that an invalid SellerFastener object raises a ValidationError."""
        data = {
            'seller_id': None,  # Missing seller_id
            'fastener_id': None,  # Missing fastener_id
            'price': -10.99,  # Invalid negative price
            'quantity': -100,  # Invalid negative quantity
        }
        serializer = SellerFastenerSerializer(data=data)
        assert not serializer.is_valid()
        assert 'seller_id' in serializer.errors
        assert 'fastener_id' in serializer.errors
        assert 'quantity' in serializer.errors
