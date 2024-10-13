import logging
from django.db.models.functions import Lower
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from fastener_app.models import Fastener
from fastener_app.serializers import FastenerSerializer

logger = logging.getLogger(__name__)


class FastenerListView(APIView):
    """
    GET /fasteners/ to retrieve all fasteners with optional sorting and filtering.
    Supports sorting by 'thread_size', which sorts by 'thread_size__metric_size_num'.
    Other sortable fields include 'material', 'finish', 'category', 'product_id', and 'description'.
    Usage example: /fasteners/?sort=thread_size:asc&filter=material:Steel&filter=finish:plain
    """

    # Define a mapping from sortable fields to ORM lookup expressions
    SORT_FIELD_MAPPING = {
        'thread_size': 'thread_size__metric_size_num',  # Changed to numeric field
        'material': 'material__name',
        'finish': 'finish__name',
        'category': 'category__name',
        'product_id': 'product_id',
        'description': 'description',
    }

    FILTER_MAPPING = {
        'material': 'material__name',
        'finish': 'finish__name',
        'category': 'category__name',
        'description': 'description',
    }

    def sort_queryset(self, queryset, sort_param):
        """
        Sort the queryset based on sort_param. Raises ValueError if the sort field or direction is invalid.
        """
        if sort_param:
            try:
                # Attempt to split sort_param into field and direction
                field, direction = sort_param.split(':')
            except ValueError:
                # Raise a ValueError if the format is incorrect
                raise ValueError(f"Invalid sort parameter format: '{sort_param}'. Expected format: 'field:direction'.")

            if field not in self.SORT_FIELD_MAPPING:
                raise ValueError(f"Cannot sort by field '{field}'.")

            # Retrieve the actual ORM field for sorting
            orm_field = self.SORT_FIELD_MAPPING[field]

            # Determine the ordering direction
            if direction == 'asc':
                ordering = orm_field
            elif direction == 'desc':
                ordering = f'-{orm_field}'
            else:
                raise ValueError("Invalid sort direction. Use 'asc' or 'desc'.")

            # Apply the ordering to the queryset
            queryset = queryset.order_by(ordering)

        return queryset

    def get_filter(self, filter_params):
        """
        Build annotation and filter dictionaries from the filter parameters.
        Raises ValueError if an invalid filter key is provided.
        """
        if not filter_params:
            return {}, {}

        filter_dict = {}
        annotation_dict = {}

        for filter_item in filter_params:
            try:
                key, value = filter_item.split(':')
            except ValueError:
                raise ValueError(f"Invalid filter format: '{filter_item}'. Expected format: 'key:value'.")

            if key not in self.FILTER_MAPPING:
                raise ValueError(f"Invalid filter key '{key}'.")

            # Use Lower() for case-insensitive filtering
            orm_field = self.FILTER_MAPPING[key]
            annotation_dict[f"{orm_field}_lower"] = Lower(orm_field)
            if f"{orm_field}_lower__in" not in filter_dict:
                filter_dict[f"{orm_field}_lower__in"] = []

            filter_dict[f"{orm_field}_lower__in"].append(value.lower())

        return annotation_dict, filter_dict

    def get(self, request):
        """
        Handle the GET request, apply filtering and sorting, and return the result.
        """
        sort_param = request.GET.get('sort')
        filter_params = request.GET.getlist('filter')

        try:
            # Process filters
            annotation_dict, filter_dict = self.get_filter(filter_params)

            # Fetch the fasteners queryset with related objects
            fasteners = Fastener.objects.select_related(
                'thread_size', 'material', 'finish', 'category'
            ).annotate(**annotation_dict).filter(**filter_dict)

            # Process sorting
            fasteners = self.sort_queryset(fasteners, sort_param)

        except ValueError as e:
            # Return an error response if sorting or filtering fails
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize and return the sorted and filtered fasteners
        serializer = FastenerSerializer(fasteners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
