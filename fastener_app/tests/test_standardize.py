import pytest
from fastener_app.standardizers import standardize_thread_size
from fastener_app.models import (
    ThreadSize,
    constants
)

@pytest.mark.django_db
def test_standardize_thread_size_metric():
    raw_data = {
        'thread_size': 'M12-1.75'
    }
    standardized_data = {}

    standardize_thread_size(raw_data, standardized_data)

    assert standardized_data['metric_size_str'] == 'M12-1.75'
    assert standardized_data['thread_type'] == constants.ThreadType.METRIC.value
    assert standardized_data['unit'] == constants.UnitType.MILLIMETER.value
    assert standardized_data['thread_per_unit'] == 1.75  # Threads per millimeter (TPM)

    # Ensure the ThreadSize instance was created in the database
    thread_size = ThreadSize.objects.get(metric_size_str='M12-1.75')
    assert thread_size.metric_size_num == 12.0
    assert thread_size.thread_per_unit == 1.75

@pytest.mark.django_db
def test_standardize_thread_size_imperial():
    raw_data = {
        'thread_size': '1/2-13'
    }
    standardized_data = {}

    standardize_thread_size(raw_data, standardized_data)

    assert standardized_data['imperial_size_str'] == '1/2-13'
    assert standardized_data['thread_type'] == constants.ThreadType.IMPERIAL.value
    assert standardized_data['unit'] == constants.UnitType.INCH.value
    assert standardized_data['thread_per_unit'] == 13  # Threads per inch (TPI)

    # Ensure the ThreadSize instance was created in the database
    thread_size = ThreadSize.objects.get(imperial_size_str='1/2-13')
    assert thread_size.imperial_size_num == 0.5
    assert thread_size.thread_per_unit == 13
