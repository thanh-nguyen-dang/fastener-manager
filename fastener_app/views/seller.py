from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.db import transaction
from fastener_app.serializers import SellerSerializer


class SellerCreateView(APIView):
    parser_classes = [JSONParser]  # Ensure the view parses JSON data

    @transaction.atomic  # Ensure atomicity, either all sellers are created or none
    def post(self, request):
        # If the data is a list (multiple sellers)
        if isinstance(request.data, list):
            # Set `many=True` to serialize multiple objects
            serializer = SellerSerializer(data=request.data, many=True)
        else:
            # Single object case
            serializer = SellerSerializer(data=request.data)

        if serializer.is_valid():
            # If data is valid, save all sellers
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
