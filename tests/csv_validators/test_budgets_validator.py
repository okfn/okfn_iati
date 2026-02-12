"""Tests for BudgetsCsvValidator."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.budgets_validator import BudgetsCsvValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestBudgetsCsvValidator(unittest.TestCase):

    def _write_csv(self, rows, columns=None):
        if columns is None:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
            columns = IatiMultiCsvConverter.csv_files['budgets']['columns']
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, newline=''
        )
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.close()
        return f.name

    def _base_row(self, **overrides):
        row = {
            'activity_identifier': 'ORG-001',
            'budget_type': '1',
            'budget_status': '2',
            'period_start': '2024-01-01',
            'period_end': '2024-12-31',
            'value': '100000',
        }
        row.update(overrides)
        return row

    def test_valid_minimal(self):
        path = self._write_csv([self._base_row()])
        try:
            v = BudgetsCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        row = {
            'activity_identifier': '',
            'budget_type': '',
            'budget_status': '',
            'period_start': '',
            'period_end': '',
            'value': '',
        }
        path = self._write_csv([row])
        try:
            v = BudgetsCsvValidator()
            result = v.validate(path)
            self.assertFalse(result.is_valid)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 6)
        finally:
            os.unlink(path)

    def test_invalid_enum(self):
        path = self._write_csv([self._base_row(budget_type='9')])
        try:
            v = BudgetsCsvValidator()
            result = v.validate(path)
            enum_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_ENUM
            ]
            self.assertTrue(len(enum_errors) > 0)
        finally:
            os.unlink(path)

    def test_invalid_dates(self):
        path = self._write_csv([self._base_row(period_start='bad', period_end='bad')])
        try:
            v = BudgetsCsvValidator()
            result = v.validate(path)
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertEqual(len(date_errors), 2)
        finally:
            os.unlink(path)

    def test_invalid_value(self):
        path = self._write_csv([self._base_row(value='abc')])
        try:
            v = BudgetsCsvValidator()
            result = v.validate(path)
            decimal_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DECIMAL
            ]
            self.assertTrue(len(decimal_errors) > 0)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
