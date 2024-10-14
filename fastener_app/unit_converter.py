import re
import fastener_app.models.constants as constants
from fractions import Fraction


def inch_to_mm(inches):
    """
    Convert inches to millimeters.
    1 inch = 25.4 millimeters
    """
    return int(inches * constants.INCH_TO_MM)  # rounding to 3 decimal places for precision


def mm_to_inch(mm):
    """
    Convert millimeters to inches.
    1 millimeter = 0.0393701 inches
    """
    return round_to_nearest_quarter(round(mm / constants.INCH_TO_MM, 3))


def round_to_nearest_quarter(decimal_value):
    return round(decimal_value * 4) / 4


def decimal_to_fraction_with_quarter_steps(decimal_value):
    """
    Convert a decimal number to the nearest fraction with 1/4 steps.
    Example: 0.34 -> 1/4, 0.68 -> 3/4, 1.14 -> 1 1/4
    """
    rounded_value = round_to_nearest_quarter(decimal_value)

    # Step 2: Convert the rounded value to a fraction
    fraction = Fraction(rounded_value).limit_denominator(4)

    # Step 3: Get the whole number and the remainder
    whole_number = int(fraction)  # Get the whole number part
    remainder = fraction - whole_number  # Get the fractional part

    # Step 4: If there's a fractional part, return the mixed fraction
    if remainder.numerator != 0:
        if whole_number > 0:
            return f"{whole_number} {remainder.numerator}/{remainder.denominator}"
        return f"{remainder.numerator}/{remainder.denominator}"
    return f"{whole_number}"


def return_all_from_imperial(match):
    imperial_size_num = parse_fraction_number(match)
    thread_per_unit = int(match.group(3))  # Threads per inch (TPI)
    metric_size_num = inch_to_mm(imperial_size_num)
    thread_per_unit_in_mm = mm_to_inch(thread_per_unit)
    return dict(
        metric_size_num = metric_size_num,
        metric_size_str = f"M{metric_size_num}-{thread_per_unit_in_mm}",
        imperial_size_num=imperial_size_num,
        thread_per_unit = thread_per_unit,
    )


def return_all_from_metric(match):
    metric_size_num = float(match.group(1))
    thread_per_unit = float(match.group(3))
    imperial_size_num = mm_to_inch(metric_size_num)
    thread_per_unit_in_inch = int(inch_to_mm(thread_per_unit))
    return dict(
        metric_size_num = metric_size_num,
        imperial_size_num = imperial_size_num,
        imperial_size_str = f"{decimal_to_fraction_with_quarter_steps(imperial_size_num)}-{thread_per_unit_in_inch}",
        thread_per_unit = thread_per_unit,
    )


def get_all_info_from_thread_size_str(size_str):
    match = re.match(constants.METRIC_REG, size_str)
    if match:
        return return_all_from_metric(match) | dict(
            metric_size_str = size_str,
            thread_type = constants.ThreadType.METRIC.value,
            unit = constants.UnitType.MILLIMETER.value,
        )
    match = re.match(constants.IMPERIAL_REG, size_str)
    if match:
        return return_all_from_imperial(match) | dict(
            imperial_size_str = size_str,
            thread_type = constants.ThreadType.IMPERIAL.value,
            unit = constants.UnitType.INCH.value,
        )
    raise ValueError(f"Invalid thread size format: {size_str}")



def metric_to_imperial_name(metric_size_str):
    match = re.match(constants.METRIC_REG, metric_size_str)
    if not match:
        return None

    other_values = return_all_from_metric(match)
    return other_values.get("imperial_size_str")


def parse_fraction_number(match):
    if '/' in match.group(1):
        # Handle fractional sizes like "1/2"
        numerator, denominator = map(int, match.group(1).split('/'))
        imperial_size_num = numerator / denominator
    else:
        # Handle whole number sizes like "1"
        imperial_size_num = float(match.group(1))
    return imperial_size_num


def imperial_to_metric_name(imperial_size_str):
    match = re.match(constants.IMPERIAL_REG, imperial_size_str)
    if not match:
        return None
    other_values = return_all_from_imperial(match)
    return other_values.get("metric_size_str")
