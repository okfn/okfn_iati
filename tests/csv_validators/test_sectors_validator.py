"""Tests for SectorsCsvValidator."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.sectors_validator import SectorsCsvValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestSectorsCsvValidator(unittest.TestCase):

    def _write_csv(self, rows, columns=None):
        if columns is None:
            from okfn_iati.activities import IatiMultiCsvConverter
            columns = IatiMultiCsvConverter.csv_files['sectors']['columns']
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
            'sector_code': '11110',
        }
        row.update(overrides)
        return row

    def test_valid_minimal(self):
        path = self._write_csv([self._base_row()])
        try:
            v = SectorsCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        path = self._write_csv([{'activity_identifier': '', 'sector_code': ''}])
        try:
            v = SectorsCsvValidator()
            result = v.validate(path)
            self.assertFalse(result.is_valid)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 2)
        finally:
            os.unlink(path)

    def test_invalid_percentage(self):
        path = self._write_csv([self._base_row(percentage='150')])
        try:
            v = SectorsCsvValidator()
            result = v.validate(path)
            pct_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_PERCENTAGE
            ]
            self.assertTrue(len(pct_errors) > 0)
        finally:
            os.unlink(path)

    def test_invalid_vocabulary(self):
        path = self._write_csv([self._base_row(vocabulary='999')])
        try:
            v = SectorsCsvValidator()
            result = v.validate(path)
            enum_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_ENUM
            ]
            self.assertTrue(len(enum_errors) > 0)
        finally:
            os.unlink(path)

    def test_valid_with_percentage(self):
        path = self._write_csv([
            self._base_row(percentage='60', vocabulary='1'),
            self._base_row(sector_code='11120', percentage='40', vocabulary='1'),
        ])
        try:
            v = SectorsCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
