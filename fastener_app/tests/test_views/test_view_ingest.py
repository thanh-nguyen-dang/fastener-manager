import pytest
import logging
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from fastener_app.models import Seller, Fastener, SellerFastener
from unittest.mock import patch, call


logger = logging.getLogger(__name__)


# Test fixtures for Seller and CSV data
@pytest.fixture
def seller(db):
    return Seller.objects.create(
        name="Test Seller",
        csv_mapping={
            'field_1': 'product_id',
            'field_2': 'description',
            'field_3': 'thread_size',
            'field_4': 'material',
            'field_5': 'finish',
            'field_6': 'category',
            'field_7': 'price',
            'field_8': 'quantity'
        }
    )


@pytest.fixture
def valid_csv_file():
    csv_content = (
        "field_1,field_2,field_3,field_4,field_5,field_6,field_7,field_8\n"
        "F001,Fastener Description,M12-1.75,Steel,Plain,Hex Cap Screw,10.50,200\n"
        "F002,Another Fastener,M10-1.5,Aluminum,Zinc,Hex Cap Screw,15.99,300\n"
    ).encode('utf-8')  # Encode the string as bytes
    return SimpleUploadedFile('fasteners.csv', csv_content, content_type='text/csv')


@pytest.fixture
def invalid_csv_file():
    # CSV with invalid price and quantity
    csv_content = (
        "field_1,field_2,field_3,field_4,field_5,field_6,field_7,field_8\n"
        "F001,Fastener Description,M12-1.75,Steel,Plain,Hex Cap Screw,invalid_price,invalid_quantity\n"
    ).encode('utf-8')
    return SimpleUploadedFile('invalid_fasteners.csv', csv_content, content_type='text/csv')


# Test case for successful CSV ingestion
@pytest.mark.django_db
def test_successful_csv_ingestion(api_client, seller, valid_csv_file):
    url = reverse('fastener-ingest', args=[seller.id])
    response = api_client.post(url, {'file': valid_csv_file}, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED
    assert Fastener.objects.filter(product_id='F001').exists()
    assert Fastener.objects.filter(product_id='F002').exists()

    seller_fastener_1 = SellerFastener.objects.get(fastener__product_id='F001')
    assert seller_fastener_1.price == pytest.approx(10.5)
    assert seller_fastener_1.quantity == 200

    seller_fastener_2 = SellerFastener.objects.get(fastener__product_id='F002')
    assert str(seller_fastener_2.price) == str(15.99)
    assert seller_fastener_2.quantity == 300


# Test case for missing file in request
@pytest.mark.django_db
def test_missing_file_in_request(api_client, seller):
    url = reverse('fastener-ingest', args=[seller.id])
    response = api_client.post(url, {}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "No file provided."


# Test case for invalid price and quantity
@pytest.mark.django_db
@patch("fastener_app.views.fastener_ingest.logger")
def test_invalid_price_and_quantity(logger, api_client, seller, invalid_csv_file):
    url = reverse('fastener-ingest', args=[seller.id])
    response = api_client.post(url, {'file': invalid_csv_file}, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED

    # Check that Fastener was created
    fastener = Fastener.objects.get(product_id='F001')
    seller_fastener = SellerFastener.objects.get(fastener=fastener)

    # Invalid price and quantity should default to 0.00 and 0
    assert seller_fastener.price == 0.00
    assert seller_fastener.quantity == 0

    # Check that logger warnings were called
    logger.warning.assert_has_calls([
        call("Invalid price value in row 1. Set to 0.00."),
        call("Invalid quantity value in row 1. Set to 0.")
    ], any_order=True)


# Test case for error handling
@pytest.mark.django_db
@patch("fastener_app.views.fastener_ingest.logger")
def test_error_handling_during_ingestion(logger, api_client, seller, valid_csv_file):
    url = reverse('fastener-ingest', args=[seller.id])

    # Simulate an error in the ingestion process by raising an exception in handle_fastener
    with patch('fastener_app.views.FastenerIngestView.handle_fastener', side_effect=Exception("Test Exception")):
        response = api_client.post(url, {'file': valid_csv_file}, format='multipart')

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data['error'] == "Failed to ingest CSV data."
    logger.error.assert_called_with("Error ingesting CSV data: Test Exception")
