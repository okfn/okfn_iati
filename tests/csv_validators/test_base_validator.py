"""Tests for csv_validators.base."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.base import BaseCsvValidator, ColumnRule
from okfn_iati.csv_validators.models import ErrorCode
from okfn_iati.csv_validators.field_validators import validate_date


class DummyValidator(BaseCsvValidator):
    """Concrete test validator using the activities CSV definition."""

    @property
    def csv_key(self):
        return 'activities'

    @property
    def column_rules(self):
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='title', required=False),
        ]


class DummyBudgetsValidator(BaseCsvValidator):
    """Concrete test validator for budgets with date validators."""

    @property
    def csv_key(self):
        return 'budgets'

    @property
    def column_rules(self):
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='period_start',
                required=True,
                validators=[(validate_date, ErrorCode.INVALID_DATE)]
            ),
        ]


class TestBaseCsvValidator(unittest.TestCase):

    def _write_csv(self, rows, columns):
        """Helper: write rows to a temp CSV and return the path."""
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, newline=''
        )
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.close()
        return f.name

    def test_missing_file(self):
        v = DummyValidator()
        result = v.validate("/nonexistent/path/activities.csv")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, ErrorCode.MISSING_FILE)

    def test_empty_file(self):
        path = self._write_csv([], ['activity_identifier', 'title'])
        try:
            v = DummyValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid)  # only a warning
            self.assertEqual(len(result.warnings), 1)
            self.assertEqual(result.warnings[0].code, ErrorCode.EMPTY_FILE)
        finally:
            os.unlink(path)

    def test_required_field_missing(self):
        path = self._write_csv(
            [{'activity_identifier': '', 'title': 'Test'}],
            ['activity_identifier', 'title']
        )
        try:
            v = DummyValidator()
            result = v.validate(path)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, ErrorCode.REQUIRED_FIELD)
            self.assertEqual(result.errors[0].column_name, 'activity_identifier')
            self.assertEqual(result.errors[0].row_number, 2)
        finally:
            os.unlink(path)

    def test_valid_rows(self):
        path = self._write_csv(
            [
                {'activity_identifier': 'ORG-001', 'title': 'Activity One'},
                {'activity_identifier': 'ORG-002', 'title': ''},
            ],
            ['activity_identifier', 'title']
        )
        try:
            v = DummyValidator()
            result = v.validate(path)
            # May have column warnings but no errors
            self.assertTrue(result.is_valid)
        finally:
            os.unlink(path)

    def test_field_validator_applied(self):
        path = self._write_csv(
            [{'activity_identifier': 'ORG-001', 'period_start': 'bad-date'}],
            ['activity_identifier', 'period_start']
        )
        try:
            v = DummyBudgetsValidator()
            result = v.validate(path)
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertTrue(len(date_errors) > 0)
            self.assertEqual(date_errors[0].column_name, 'period_start')
        finally:
            os.unlink(path)

    def test_field_validator_skipped_on_empty(self):
        """Non-required fields with validators should not fire on empty."""
        path = self._write_csv(
            [{'activity_identifier': 'ORG-001', 'period_start': ''}],
            ['activity_identifier', 'period_start']
        )
        try:
            v = DummyBudgetsValidator()
            result = v.validate(path)
            # period_start is required so we get REQUIRED_FIELD, not INVALID_DATE
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertEqual(len(date_errors), 0)
        finally:
            os.unlink(path)

    def test_missing_column_warning(self):
        """Warn about expected columns missing from the CSV header."""
        path = self._write_csv(
            [{'activity_identifier': 'ORG-001'}],
            ['activity_identifier']
        )
        try:
            v = DummyBudgetsValidator()
            result = v.validate(path)
            col_warnings = [
                w for w in result.warnings if w.code == ErrorCode.MISSING_COLUMN
            ]
            # budgets has several expected columns, at least some should be missing
            self.assertTrue(len(col_warnings) > 0)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
