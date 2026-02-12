"""Tests for csv_validators.field_validators."""

import unittest

from okfn_iati.csv_validators.field_validators import (
    validate_required, validate_date, validate_datetime_iso,
    validate_integer, validate_decimal, validate_enum,
    validate_percentage, validate_boolean_flag, validate_url,
    validate_currency, validate_language, validate_crs_code
)
from okfn_iati.enums import (
    ActivityStatus, BudgetType, TransactionType, OrganisationType
)


class TestValidateRequired(unittest.TestCase):

    def test_valid_value(self):
        self.assertIsNone(validate_required("hello"))

    def test_empty_string(self):
        self.assertIsNotNone(validate_required(""))

    def test_whitespace_only(self):
        self.assertIsNotNone(validate_required("   "))

    def test_none(self):
        self.assertIsNotNone(validate_required(None))


class TestValidateDate(unittest.TestCase):

    def test_valid_date(self):
        self.assertIsNone(validate_date("2024-01-15"))

    def test_invalid_format(self):
        self.assertIsNotNone(validate_date("15-01-2024"))

    def test_invalid_date(self):
        self.assertIsNotNone(validate_date("2024-13-01"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_date(""))
        self.assertIsNone(validate_date(None))

    def test_just_year(self):
        self.assertIsNotNone(validate_date("2024"))


class TestValidateDatetimeIso(unittest.TestCase):

    def test_plain_date(self):
        self.assertIsNone(validate_datetime_iso("2024-01-15"))

    def test_datetime_with_z(self):
        self.assertIsNone(validate_datetime_iso("2024-01-15T10:30:00Z"))

    def test_datetime_with_offset(self):
        self.assertIsNone(validate_datetime_iso("2024-01-15T10:30:00+05:00"))

    def test_invalid(self):
        self.assertIsNotNone(validate_datetime_iso("not-a-date"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_datetime_iso(""))


class TestValidateInteger(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_integer("42"))
        self.assertIsNone(validate_integer("-1"))
        self.assertIsNone(validate_integer("0"))

    def test_invalid(self):
        self.assertIsNotNone(validate_integer("3.14"))
        self.assertIsNotNone(validate_integer("abc"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_integer(""))
        self.assertIsNone(validate_integer(None))


class TestValidateDecimal(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_decimal("3.14"))
        self.assertIsNone(validate_decimal("42"))
        self.assertIsNone(validate_decimal("-100.5"))

    def test_invalid(self):
        self.assertIsNotNone(validate_decimal("abc"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_decimal(""))


class TestValidateEnum(unittest.TestCase):

    def test_valid_int_enum(self):
        # ActivityStatus is IntEnum (1, 2, 3, ...)
        self.assertIsNone(validate_enum("2", ActivityStatus))

    def test_invalid_int_enum(self):
        self.assertIsNotNone(validate_enum("99", ActivityStatus))

    def test_valid_string_enum(self):
        # BudgetType values are "1", "2"
        self.assertIsNone(validate_enum("1", BudgetType))

    def test_invalid_string_enum(self):
        self.assertIsNotNone(validate_enum("Z", BudgetType))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_enum("", ActivityStatus))
        self.assertIsNone(validate_enum(None, ActivityStatus))

    def test_transaction_type(self):
        self.assertIsNone(validate_enum("3", TransactionType))
        self.assertIsNotNone(validate_enum("99", TransactionType))

    def test_organisation_type(self):
        self.assertIsNone(validate_enum("10", OrganisationType))
        self.assertIsNone(validate_enum("70", OrganisationType))


class TestValidatePercentage(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_percentage("50"))
        self.assertIsNone(validate_percentage("0"))
        self.assertIsNone(validate_percentage("100"))
        self.assertIsNone(validate_percentage("33.33"))

    def test_out_of_range(self):
        self.assertIsNotNone(validate_percentage("-1"))
        self.assertIsNotNone(validate_percentage("101"))

    def test_not_a_number(self):
        self.assertIsNotNone(validate_percentage("abc"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_percentage(""))


class TestValidateBooleanFlag(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_boolean_flag("0"))
        self.assertIsNone(validate_boolean_flag("1"))
        self.assertIsNone(validate_boolean_flag("true"))
        self.assertIsNone(validate_boolean_flag("false"))
        self.assertIsNone(validate_boolean_flag("True"))
        self.assertIsNone(validate_boolean_flag("FALSE"))

    def test_invalid(self):
        self.assertIsNotNone(validate_boolean_flag("yes"))
        self.assertIsNotNone(validate_boolean_flag("2"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_boolean_flag(""))


class TestValidateUrl(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_url("http://example.com"))
        self.assertIsNone(validate_url("https://example.com/path"))

    def test_invalid(self):
        self.assertIsNotNone(validate_url("ftp://example.com"))
        self.assertIsNotNone(validate_url("example.com"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_url(""))


class TestValidateCurrency(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_currency("USD"))
        self.assertIsNone(validate_currency("EUR"))

    def test_invalid(self):
        self.assertIsNotNone(validate_currency("usd"))
        self.assertIsNotNone(validate_currency("US"))
        self.assertIsNotNone(validate_currency("USDX"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_currency(""))


class TestValidateLanguage(unittest.TestCase):

    def test_valid(self):
        self.assertIsNone(validate_language("en"))
        self.assertIsNone(validate_language("es"))

    def test_invalid(self):
        self.assertIsNotNone(validate_language("EN"))
        self.assertIsNotNone(validate_language("eng"))
        self.assertIsNotNone(validate_language("e"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_language(""))


class TestValidateCrsCode(unittest.TestCase):

    def test_valid_code(self):
        # 10000 is a known CRS channel code (Public Sector Institutions)
        self.assertIsNone(validate_crs_code("10000"))

    def test_invalid_code(self):
        self.assertIsNotNone(validate_crs_code("XXXXX"))

    def test_empty_is_ok(self):
        self.assertIsNone(validate_crs_code(""))
        self.assertIsNone(validate_crs_code(None))


if __name__ == '__main__':
    unittest.main()
