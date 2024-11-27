# utils/misc/validators.py

import re
from datetime import datetime

# Regular expression for validating full names
full_name_pattern = re.compile(r"^[A-Z][a-z]*([-'\s][A-Z][a-z]*)*$")

# Regular expression to match DD/MM/YYYY format within the range of 1970 to 2010
dob_pattern = re.compile(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19[7-9][0-9]|200[0-9]|2010)$")

# Regular expression for Uzbekistan phone numbers
uzbekistan_phone_pattern = re.compile(r"^(?:\+998|998)(?:[0-9]{2})\s?[0-9]{3}\s?[0-9]{4}$")

def validate_full_name(name):
    return bool(full_name_pattern.match(name))

def validate_dob(dob):
    if not dob_pattern.match(dob):
        return False
    try:
        dob_date = datetime.strptime(dob, "%d/%m/%Y")
        return datetime(1970, 1, 1) <= dob_date <= datetime(2010, 12, 31)
    except ValueError:
        return False

def validate_uzbekistan_phone(phone):
    return bool(uzbekistan_phone_pattern.match(phone))
