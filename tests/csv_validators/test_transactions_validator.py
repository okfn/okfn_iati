"""Tests for TransactionsCsvValidator."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.transactions_validator import TransactionsCsvValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestTransactionsCsvValidator(unittest.TestCase):

    def _write_csv(self, rows, columns=None):
        if columns is None:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
            columns = IatiMultiCsvConverter.csv_files['transactions']['columns']
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
            'transaction_type': '3',
            'transaction_date': '2024-06-15',
            'value': '50000',
        }
        row.update(overrides)
        return row

    def test_valid_minimal(self):
        path = self._write_csv([self._base_row()])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        row = {
            'activity_identifier': '',
            'transaction_type': '',
            'transaction_date': '',
            'value': '',
        }
        path = self._write_csv([row])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            self.assertFalse(result.is_valid)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 4)
        finally:
            os.unlink(path)

    def test_invalid_transaction_type(self):
        path = self._write_csv([self._base_row(transaction_type='99')])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            enum_errors = [
                e for e in result.errors
                if e.code == ErrorCode.INVALID_ENUM
                and e.column_name == 'transaction_type'
            ]
            self.assertTrue(len(enum_errors) > 0)
        finally:
            os.unlink(path)

    def test_invalid_date(self):
        path = self._write_csv([self._base_row(transaction_date='bad')])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertTrue(len(date_errors) > 0)
        finally:
            os.unlink(path)

    def test_invalid_value(self):
        path = self._write_csv([self._base_row(value='not-a-number')])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            decimal_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DECIMAL
            ]
            self.assertTrue(len(decimal_errors) > 0)
        finally:
            os.unlink(path)

    def test_valid_with_optionals(self):
        row = self._base_row(
            currency='USD',
            value_date='2024-06-15',
            description='Test payment',
            description_lang='en',
            flow_type='10',
            finance_type='110',
            aid_type_vocabulary='1',
            tied_status='5',
            humanitarian='0',
        )
        path = self._write_csv([row])
        try:
            v = TransactionsCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
