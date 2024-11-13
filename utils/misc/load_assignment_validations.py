import re

def validate_truck_number(truck_number):
    """
    Validates the truck number format.
    - The truck number should contain only numbers, or
    - It may contain one alphabet character either at the beginning or end.

    Returns True if valid, False otherwise.
    """
    pattern = r'^[A-Za-z]?\d+[A-Za-z]?$'
    return bool(re.match(pattern, truck_number))

def validate_load_number(load_number):
    """
    Validates the load number format.
    - It can contain only numbers, only alphabets, or a combination of both.
    - No symbols or special characters allowed.

    Returns True if valid, False otherwise.
    """
    pattern = r'^[A-Za-z0-9]+$'
    return bool(re.match(pattern, load_number))

def validate_broker_name(broker_name):
    """
    Validates the broker name format.
    - It must contain only alphabetic characters.
    - Allows multiple words separated by a single space.
    - No numbers, symbols, or special characters allowed.

    Returns True if valid, False otherwise.
    """
    pattern = r'^[A-Za-z]+(?: [A-Za-z]+)*$'
    return bool(re.match(pattern, broker_name))

def validate_location(location):
    """
    Validates the location format.
    - Allows letters, numbers, spaces, and commas for complex locations.
    - Requires the location to end with a ZIP code in the format: 12345 or 12345-6789.

    Returns True if valid, False otherwise.
    """
    pattern = r'^[A-Za-z0-9\s]+(?:, [A-Za-z0-9\s]+)*, \d{5}(-\d{4})?$'
    return bool(re.match(pattern, location))


def validate_datetime_us(datetime_str):
    """
    Validates datetime format in 'MM/DD/YYYY HH:MM' for USA format.
    Returns True if valid, False otherwise.
    """
    pattern = r'^(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])\/\d{4} (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, datetime_str))


def validate_datetime_range_us(datetime_range_str):
    """
    Validates datetime range format in 'MM/DD/YYYY HH:MM - HH:MM' for USA format.
    Returns True if valid, False otherwise.
    """
    pattern = r'^(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])\/\d{4} (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] - (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, datetime_range_str))


# Regular expression pattern for validating positive numerical values (integer or decimal)
loaded_miles_pattern = r"^\d+(\.\d+)?$"

def validate_loaded_miles(miles: str) -> bool:
    """
    Validates that the input is a positive numerical value (integer or decimal).
    Returns True if valid, otherwise False.
    """
    return bool(re.match(loaded_miles_pattern, miles))
