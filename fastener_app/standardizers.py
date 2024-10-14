from fastener_app.models import (
    Material,
    Finish,
    ThreadSize,
    Category,
    constants
)
from fastener_app.tests.test_views.test_view_ingest import logger
from fastener_app.unit_converter import get_all_info_from_thread_size_str


def standardize_description(raw_data, standardized_data):
    if 'description' in raw_data:
        description = ' '.join(raw_data['description'].strip().upper().split())
        standardized_data['description'] = description


def parse_size(raw_data, standardized_data):
    """
    Extract numeric value from metric_size_str and the number of threads per millimeter.
    Example: "M12-1.75" -> (12.0, 1.75) where 1.75 is TPM (Threads Per Millimeter).
    Update the standardized_data dictionary with metric thread details.
    """
    metric_size_str = raw_data.get('thread_size', None)
    if not metric_size_str:
        return

    if metric_size_str.startswith('M'):
        metric_size_str = metric_size_str.replace('/', '-')

    standardized_data.update(get_all_info_from_thread_size_str(metric_size_str))


def standardize_thread_size(raw_data, standardized_data):
    """
    Standardize thread size from raw_data and store in standardized_data.
    Handles both metric and imperial sizes, setting appropriate thread type, size, and unit.
    """

    # Parse metric and imperial sizes
    parse_size(raw_data, standardized_data)

    # Store or update ThreadSize entry in the database
    thread_size_obj, _ = ThreadSize.objects.get_or_create(
        metric_size_str=standardized_data.get('metric_size_str'),
        imperial_size_str=standardized_data.get('imperial_size_str'),
        defaults={
            'name': standardized_data['metric_size_str'] or standardized_data['imperial_size_str'],
            'thread_type': standardized_data['thread_type'],
            'unit': standardized_data['unit'],
            'metric_size_num': standardized_data.get('metric_size_num'),
            'imperial_size_num': standardized_data.get('imperial_size_num'),
            'thread_per_unit': standardized_data.get('thread_per_unit'),  # Same field for both TPM and TPI
        }
    )

    # Add the thread size id to standardized_data
    standardized_data['thread_size'] = thread_size_obj


def standardize_material(raw_data, standardized_data):
    if 'material' in raw_data:
        material_name = raw_data['material'].strip().title()
        material, _ = Material.objects.get_or_create(name=material_name)
        logger.debug(material_name)
        logger.debug(material)
        standardized_data['material'] = material

def standardize_finish(raw_data, standardized_data):
    if 'finish' in raw_data:
        finish_name = raw_data['finish'].strip().title()
        finish, _ = Finish.objects.get_or_create(name=finish_name)
        standardized_data['finish'] = finish

def standardize_category(raw_data, standardized_data):
    if 'category' in raw_data:
        category_name = raw_data['category'].strip().title()
        category, _ = Category.objects.get_or_create(name=category_name)
        standardized_data['category'] = category

def standardize_product_id(raw_data, standardized_data):
    if 'product_id' in raw_data:
        standardized_data['product_id'] = raw_data['product_id']
