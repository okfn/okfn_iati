"""Tests for ActivitiesCsvValidator."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.activities_validator import ActivitiesCsvValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestActivitiesCsvValidator(unittest.TestCase):

    def _write_csv(self, rows, columns=None):
        if columns is None:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
            columns = IatiMultiCsvConverter.csv_files['activities']['columns']
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
            'title': 'Test Activity',
            'activity_status': '2',
            'reporting_org_ref': 'ORG',
        }
        row.update(overrides)
        return row

    def test_valid_minimal(self):
        path = self._write_csv([self._base_row()])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_missing_required_fields(self):
        row = {
            'activity_identifier': '',
            'title': '',
            'activity_status': '',
            'reporting_org_ref': '',
        }
        path = self._write_csv([row])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            self.assertFalse(result.is_valid)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 4)
        finally:
            os.unlink(path)

    def test_invalid_activity_status(self):
        path = self._write_csv([self._base_row(activity_status='99')])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            enum_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_ENUM
            ]
            self.assertTrue(len(enum_errors) > 0)
            self.assertEqual(enum_errors[0].column_name, 'activity_status')
        finally:
            os.unlink(path)

    def test_invalid_date(self):
        path = self._write_csv([self._base_row(planned_start_date='not-a-date')])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertTrue(len(date_errors) > 0)
        finally:
            os.unlink(path)

    def test_invalid_currency(self):
        path = self._write_csv([self._base_row(default_currency='xx')])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            curr_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_CURRENCY
            ]
            self.assertTrue(len(curr_errors) > 0)
        finally:
            os.unlink(path)

    def test_valid_with_all_fields(self):
        row = self._base_row(
            title_lang='en',
            description='A description',
            description_lang='en',
            activity_scope='4',
            default_currency='USD',
            humanitarian='1',
            hierarchy='1',
            last_updated_datetime='2024-01-01T10:00:00Z',
            xml_lang='en',
            reporting_org_name='Org Name',
            reporting_org_name_lang='en',
            reporting_org_type='10',
            reporting_org_role='4',
            planned_start_date='2024-01-01',
            actual_start_date='2024-01-15',
            planned_end_date='2025-12-31',
            collaboration_type='1',
            default_flow_type='10',
            default_finance_type='110',
            default_aid_type_vocabulary='1',
            default_tied_status='5',
            conditions_attached='0',
        )
        path = self._write_csv([row])
        try:
            v = ActivitiesCsvValidator()
            result = v.validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
