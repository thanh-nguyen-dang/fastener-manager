import csv
import io
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from fastener_app.models import Seller, Fastener, SellerFastener
from fastener_app.standardizers import (
    standardize_description,
    standardize_thread_size,
    standardize_material,
    standardize_finish,
    standardize_category,
    standardize_product_id,
)

logger = logging.getLogger(__name__)


class FastenerIngestView(APIView):
    parser_classes = [MultiPartParser]

    def handle_fastener(self, standardized_data):
        # Dynamically retrieve fields from Fastener model's _meta
        fastener_fields = [
            field.name for field in Fastener._meta.get_fields()
            if field.name in ['description', 'thread_size', 'material', 'finish', 'category']
        ]

        # Build defaults dictionary using dictionary comprehension
        defaults = {field: standardized_data[field] for field in fastener_fields if field in standardized_data}

        # Create or update Fastener
        fastener, created = Fastener.objects.get_or_create(
            product_id=standardized_data['product_id'],
            defaults=defaults
        )

        if not created:
            # Update existing Fastener using setattr
            for field in fastener_fields:
                if field in standardized_data:
                    setattr(fastener, field, standardized_data[field])
            fastener.save()
            logger.debug(f"Updated Fastener: {fastener.product_id}")
        else:
            logger.debug(f"Created Fastener: {fastener.product_id}")
        return fastener

    def handle_fastener_seller(self, seller, fastener, row, index):
        # Handle price and quantity with validation
        try:
            price = float(row.get('price', '0.00'))
        except ValueError:
            price = 0.00
            logger.warning(f"Invalid price value in row {index}. Set to 0.00.")

        try:
            quantity = int(row.get('quantity', '0'))
        except ValueError:
            quantity = 0
            logger.warning(f"Invalid quantity value in row {index}. Set to {quantity}.")

        # Create or update SellerFastener entry
        SellerFastener.objects.update_or_create(
            seller=seller,
            fastener=fastener,
            defaults={
                'price': price,
                'quantity': quantity
            }
        )
        logger.debug(f"Updated SellerFastener for Fastener: {fastener.product_id}")

    def post(self, request, seller_id):
        seller = get_object_or_404(Seller, id=seller_id)
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            csv_file = io.TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for index, row in enumerate(reader, start=1):
                logger.debug(f"Processing row {index}: {row}")
                standardized_data = {}
                # Use the seller's csv_mapping to map raw CSV columns to model fields
                csv_mapping = seller.csv_mapping  # e.g., {'field_1': 'product_id', ...}
                mapped_data = {model_field: row.get(csv_field, '').strip() for csv_field, model_field in csv_mapping.items()}

                # Standardize the mapped data
                standardize_description(mapped_data, standardized_data)
                standardize_thread_size(mapped_data, standardized_data)
                standardize_material(mapped_data, standardized_data)
                standardize_finish(mapped_data, standardized_data)
                standardize_category(mapped_data, standardized_data)
                standardize_product_id(mapped_data, standardized_data)

                fastener = self.handle_fastener(standardized_data)
                self.handle_fastener_seller(seller, fastener, mapped_data, index)

            return Response({"status": "CSV data ingested successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error ingesting CSV data: {e}")
            return Response({"error": "Failed to ingest CSV data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
