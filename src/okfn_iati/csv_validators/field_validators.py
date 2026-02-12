"""
Pure field-validation functions for CSV cell values.

Each function takes a string value and returns None if valid,
or an error message string if invalid. These are stateless and composable.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Optional, Type

from okfn_iati.validators import crs_channel_code_validator


def validate_required(value: str) -> Optional[str]:
    """Check that value is non-empty after stripping whitespace."""
    if value is None or str(value).strip() == "":
        return "Value is required"
    return None


def validate_date(value: str) -> Optional[str]:
    """Validate ISO 8601 date format YYYY-MM-DD."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return f"Invalid date format '{value}', expected YYYY-MM-DD"
    return None


def validate_datetime_iso(value: str) -> Optional[str]:
    """Validate ISO 8601 datetime (with optional time component)."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    # Accept plain date
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return None
    except ValueError:
        pass
    # Accept datetime with various ISO formats
    dt_to_validate = value.replace('Z', '+00:00')
    if '.' in dt_to_validate:
        dt_to_validate = re.sub(r'(\.\d{6})\d+', r'\1', dt_to_validate)
    try:
        datetime.fromisoformat(dt_to_validate)
        return None
    except ValueError:
        return f"Invalid datetime format '{value}'"


def validate_integer(value: str) -> Optional[str]:
    """Validate that value is an integer."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    try:
        int(value)
    except ValueError:
        return f"Invalid integer '{value}'"
    return None


def validate_decimal(value: str) -> Optional[str]:
    """Validate that value is a decimal number."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    try:
        float(value)
    except ValueError:
        return f"Invalid decimal number '{value}'"
    return None


def validate_enum(value: str, enum_class: Type[Enum]) -> Optional[str]:
    """Validate value against an Enum class.

    Works with both string Enum and IntEnum. Compares against
    enum member values (not names).
    """
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    valid_values = []
    for member in enum_class:
        valid_values.append(str(member.value))
    if value not in valid_values:
        return (
            f"Invalid value '{value}' for {enum_class.__name__}. "
            f"Valid values: {valid_values}"
        )
    return None


def validate_percentage(value: str) -> Optional[str]:
    """Validate that value is a decimal between 0 and 100."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    try:
        num = float(value)
    except ValueError:
        return f"Invalid percentage '{value}', expected a number"
    if num < 0 or num > 100:
        return f"Percentage '{value}' is out of range 0-100"
    return None


def validate_boolean_flag(value: str) -> Optional[str]:
    """Validate boolean flag: '0', '1', 'true', 'false', or empty."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip().lower()
    if value not in ("0", "1", "true", "false"):
        return f"Invalid boolean flag '{value}', expected 0, 1, true, or false"
    return None


def validate_url(value: str) -> Optional[str]:
    """Validate URL starts with http:// or https://."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    if not value.startswith(("http://", "https://")):
        return f"Invalid URL '{value}', must start with http:// or https://"
    return None


def validate_currency(value: str) -> Optional[str]:
    """Validate 3-letter uppercase ISO 4217 currency code."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    if not re.match(r'^[A-Z]{3}$', value):
        return f"Invalid currency code '{value}', expected 3-letter uppercase code"
    return None


def validate_language(value: str) -> Optional[str]:
    """Validate 2-letter lowercase ISO 639-1 language code."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    if not re.match(r'^[a-z]{2}$', value):
        return f"Invalid language code '{value}', expected 2-letter lowercase code"
    return None


def validate_crs_code(value: str) -> Optional[str]:
    """Validate CRS channel code using existing CRSChannelCodeValidator."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    if not crs_channel_code_validator.is_valid_code(value):
        return f"Invalid CRS channel code '{value}'"
    return None
