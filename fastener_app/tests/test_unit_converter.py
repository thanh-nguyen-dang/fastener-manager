import pytest
import re
from fastener_app.unit_converter import (
    inch_to_mm, mm_to_inch, decimal_to_fraction_with_quarter_steps,
    get_all_info_from_thread_size_str,
    imperial_to_metric_name, metric_to_imperial_name, parse_fraction_number,
    round_to_nearest_quarter
)
from fastener_app.models import constants

# Define any global constants as fixtures
@pytest.fixture
def metric_size_str():
    return "M12-1.75"

@pytest.fixture
def imperial_size_str():
    return "1/2-13"

@pytest.fixture
def invalid_size_str():
    return "invalid-size"

@pytest.fixture
def constants_fixture():
    return constants

# Test for inch to mm conversion
def test_inch_to_mm():
    assert inch_to_mm(1) == 25
    assert inch_to_mm(0.5) == 12
    assert inch_to_mm(0) == 0

# Test for mm to inch conversion
def test_mm_to_inch():
    assert mm_to_inch(25.4) == 1
    assert mm_to_inch(12.7) == 0.5
    assert mm_to_inch(0) == 0

# Test for decimal to fraction with quarter steps
def test_decimal_to_fraction_with_quarter_steps():
    assert decimal_to_fraction_with_quarter_steps(0.34) == "1/4"
    assert decimal_to_fraction_with_quarter_steps(0.68) == "3/4"
    assert decimal_to_fraction_with_quarter_steps(1.14) == "1 1/4"
    assert decimal_to_fraction_with_quarter_steps(0.25) == "1/4"
    assert decimal_to_fraction_with_quarter_steps(2.00) == "2"

# Test for parsing metric thread size
def test_get_all_info_from_thread_size_str_metric(metric_size_str):
    result = get_all_info_from_thread_size_str(metric_size_str)
    assert result['metric_size_num'] == 12
    assert result['thread_type'] == constants.ThreadType.METRIC.value
    assert result['unit'] == constants.UnitType.MILLIMETER.value
    assert result['metric_size_str'] == metric_size_str

# Test for parsing imperial thread size
def test_get_all_info_from_thread_size_str_imperial(imperial_size_str):
    result = get_all_info_from_thread_size_str(imperial_size_str)
    assert result['imperial_size_num'] == 0.5
    assert result['thread_per_unit'] == 13
    assert result['metric_size_num'] == 12
    assert result['thread_type'] == constants.ThreadType.IMPERIAL.value
    assert result['unit'] == constants.UnitType.INCH.value
    assert result['imperial_size_str'] == imperial_size_str

# Test for invalid thread size string
def test_invalid_thread_size_str(invalid_size_str):
    with pytest.raises(ValueError, match=f"Invalid thread size format: {invalid_size_str}"):
        get_all_info_from_thread_size_str(invalid_size_str)

# Test imperial to metric conversion
def test_imperial_to_metric_name(imperial_size_str):
    result = imperial_to_metric_name(imperial_size_str)
    assert result == "M12-0.5"

# Test metric to imperial conversion
def test_metric_to_imperial_name(metric_size_str):
    result = metric_to_imperial_name(metric_size_str)
    assert result == "1/2-44"

def test_invalid_metric_to_imperial_name(metric_size_str):
    result = metric_to_imperial_name("invalid-metric")
    assert result is None

# Test parsing of fraction numbers in imperial thread sizes
def test_parse_fraction_number():
    # Test with a fractional size
    size_str = "1/2-13"
    match = re.match(r'(\d+/\d+)-(\d+)', size_str)
    assert match is not None
    assert parse_fraction_number(match) == 0.5

    # Test with a whole number size
    size_str = "1-8"
    match = re.match(r'(\d+)-(\d+)', size_str)
    assert match is not None
    assert parse_fraction_number(match) == 1.0

def test_round_to_nearest_quarter():
    assert round_to_nearest_quarter(0.512) == 0.5
    assert round_to_nearest_quarter(1.13) == 1.25
    assert round_to_nearest_quarter(1.68) == 1.75
    assert round_to_nearest_quarter(1.99) == 2.0
