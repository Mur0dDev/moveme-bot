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
