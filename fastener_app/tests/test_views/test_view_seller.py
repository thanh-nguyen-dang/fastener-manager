from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from fastener_app.models import Seller
from fastener_app.serializers import SellerSerializer

class SellerCreateViewTest(TestCase):
    def setUp(self):
        # Setup the client for making API requests
        self.client = APIClient()
        self.valid_single_data = {
            "name": "Seller A",
            "contact_email": "sellerA@example.com",
            "phone_number": "+123456789",
            "address": "246 Bosch Street, Berlin City, Germany",
            "csv_mapping": {
                "item_number": "product_id",
                "product_name": "description",
                "threading": "thread_size",
                "composition": "material",
                "surface_treatment": "finish",
                "product_category": "category",
                "unit_cost": "price",
                "stock": "quantity"
            }

        }
        self.invalid_single_data = {
            "name": "",  # Invalid because the name is empty
            "contact_email": "invalid-email",  # Invalid email format
            "phone_number": "+123456789",
            "address": "123 Acme Street, Acme City, AC",
            "csv_mapping": {
                "product_id": "product_id",
                "description": "description",
                "thread_size": "thread_size",
                "material": "material",
                "finish": "finish",
                "category": "category",
                "price": "price",
                "quantity": "quantity"
            }
        }
        self.valid_multiple_data = [
            {
                "name": "Seller B",
                "contact_email": "sellerB@example.com",
                "address": "123 Acme Street, Acme City, AC",
                "phone_number": "+123456789",
                "csv_mapping": {
                    "product_id": "product_id",
                    "description": "description",
                    "thread_size": "thread_size",
                    "material": "material",
                    "finish": "finish",
                    "category": "category",
                    "price": "price",
                    "quantity": "quantity"
                }
            },
            {
                "name": "Seller C",
                "contact_email": "sellerC@example.com",
                "address": "123 Acme Street, Acme City, AC",
                "phone_number": "+123456789",
                "csv_mapping": {
                    "product_id": "product_id",
                    "description": "description",
                    "thread_size": "thread_size",
                    "material": "material",
                    "finish": "finish",
                    "category": "category",
                    "price": "price",
                    "quantity": "quantity"
                }
            }
        ]
        self.invalid_multiple_data = [
            {
                "name": "Seller D",
                "contact_email": "sellerD@example.com",
                "address": "123 Acme Street, Acme City, AC",
                "phone_number": "+123456789",
                "csv_mapping": {
                    "product_id": "product_id",
                    "description": "description",
                    "thread_size": "thread_size",
                    "material": "material",
                    "finish": "finish",
                    "category": "category",
                    "price": "price",
                    "quantity": "quantity"
                }
            },
            {
                "name": "",
                "contact_email": "invalid-email@gmail.com",
                "address": "123 Acme Street, Acme City, AC",
                "phone_number": "+123456789",
                "csv_mapping": {
                    "product_id": "product_id",
                    "material": "material",
                    "finish": "finish",
                    "category": "category",
                    "price": "price",
                    "quantity": "quantity"
                }
            }  # Invalid seller
        ]

        # Reverse URL for the seller creation view
        self.url = reverse('seller-create')

    def test_create_single_seller_valid(self):
        # Test case for creating a single valid seller
        response = self.client.post(self.url, self.valid_single_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seller.objects.count(), 1)
        self.assertEqual(Seller.objects.get().name, 'Seller A')

    def test_create_single_seller_invalid(self):
        # Test case for creating a single invalid seller
        response = self.client.post(self.url, self.invalid_single_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seller.objects.count(), 0)  # Ensure no seller is created

    def test_create_multiple_sellers_valid(self):
        # Test case for creating multiple valid sellers
        response = self.client.post(self.url, self.valid_multiple_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seller.objects.count(), 2)
        self.assertEqual(Seller.objects.first().name, 'Seller B')

    def test_create_multiple_sellers_invalid(self):
        # Test case for creating multiple sellers where one is invalid
        response = self.client.post(self.url, self.invalid_multiple_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seller.objects.count(), 0)  # Ensure atomicity, no sellers created

    def test_create_multiple_sellers_partial_failure(self):
        # Test case ensuring atomicity is preserved even when one invalid seller is present
        response = self.client.post(self.url, self.invalid_multiple_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seller.objects.count(), 0)  # No sellers should be saved due to atomicity

    def test_response_data_single_seller(self):
        # Test response data structure for a single valid seller
        response = self.client.post(self.url, self.valid_single_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Validate the response structure
        expected_data = SellerSerializer(Seller.objects.get()).data
        self.assertEqual(response.data, expected_data)

    def test_response_data_multiple_sellers(self):
        # Test response data structure for multiple valid sellers
        response = self.client.post(self.url, self.valid_multiple_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sellers = Seller.objects.all()
        expected_data = SellerSerializer(sellers, many=True).data
        self.assertEqual(response.data, expected_data)
