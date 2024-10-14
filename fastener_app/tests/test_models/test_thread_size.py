import pytest
from django.core.exceptions import ValidationError
from fastener_app.models import ThreadSize
import fastener_app.models.constants as constants


@pytest.mark.django_db
class TestThreadSizeModel:

    def test_valid_thread_size(self):
        """Test successful creation of a valid ThreadSize object."""
        thread_size = ThreadSize.objects.create(
            name="M12",
            thread_type=constants.ThreadType.METRIC.value,
            unit=constants.UnitType.MILLIMETER.value,
            metric_size_str="M12-1.75",
            metric_size_num=12.0,
            imperial_size_str="1/2-13",
            imperial_size_num=0.5,
            thread_per_unit=13.0
        )
        assert thread_size.metric_size_str == "M12-1.75"
        assert thread_size.imperial_size_num == 0.5
        assert thread_size.thread_per_unit == 13.0

    def test_invalid_metric_size_str_format(self):
        """Test that invalid metric size format raises ValidationError."""
        thread_size = ThreadSize(
            name="M12",
            thread_type=constants.ThreadType.METRIC.value,
            unit=constants.UnitType.MILLIMETER.value,
            metric_size_str="M12-invalid",  # Invalid format
            metric_size_num=12.0,
            thread_per_unit=13.0
        )
        with pytest.raises(ValidationError, match="Value M12-invalid is not a valid metric_size_str format"):
            thread_size.validate()

    def test_invalid_imperial_size_str_format(self):
        """Test that invalid imperial size format raises ValidationError."""
        thread_size = ThreadSize(
            name="Imperial Size",
            thread_type=constants.ThreadType.IMPERIAL.value,
            unit=constants.UnitType.INCH.value,
            imperial_size_str="invalid-1/2",  # Invalid format
            imperial_size_num=0.5,
            thread_per_unit=13.0
        )
        with pytest.raises(ValidationError, match="Value invalid-1/2 is not a valid imperial_size_str format"):
            thread_size.validate()

    def test_negative_metric_size_num(self):
        """Test that non-positive metric_size_num raises ValidationError."""
        thread_size = ThreadSize(
            name="M12",
            thread_type=constants.ThreadType.METRIC.value,
            unit=constants.UnitType.MILLIMETER.value,
            metric_size_num=-12.0,  # Invalid negative value
            thread_per_unit=13.0
        )
        with pytest.raises(ValidationError, match="Metric size must be a positive number"):
            thread_size.validate()

    def test_negative_imperial_size_num(self):
        """Test that non-positive imperial_size_num raises ValidationError."""
        thread_size = ThreadSize(
            name="Imperial Size",
            thread_type=constants.ThreadType.IMPERIAL.value,
            unit=constants.UnitType.INCH.value,
            imperial_size_num=-0.5,  # Invalid negative value
            thread_per_unit=13.0
        )
        with pytest.raises(ValidationError, match="Imperial size must be a positive number"):
            thread_size.validate()

    def test_zero_thread_per_unit(self):
        """Test that thread_per_unit being 0 raises ValidationError."""
        thread_size = ThreadSize(
            name="Zero Thread Size",
            thread_type=constants.ThreadType.METRIC.value,
            unit=constants.UnitType.MILLIMETER.value,
            metric_size_num=12.0,
            thread_per_unit=0.0  # Invalid zero value
        )
        with pytest.raises(ValidationError, match="Thread per unit .* must be a positive number"):
            thread_size.validate()

    def test_save_calls_validate(self):
        """Test that the save method calls the validate method."""
        thread_size = ThreadSize(
            name="M12",
            thread_type=constants.ThreadType.METRIC.value,
            unit=constants.UnitType.MILLIMETER.value,
            metric_size_str="M12-1.75",
            metric_size_num=12.0,
            imperial_size_str="1/2-13",
            imperial_size_num=0.5,
            thread_per_unit=13.0
        )
        # Save should internally call validate
        thread_size.save()
        assert ThreadSize.objects.count() == 1
