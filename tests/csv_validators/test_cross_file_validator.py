"""Tests for CrossFileValidator."""

import unittest

from okfn_iati.csv_validators.cross_file_validator import CrossFileValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestCrossFileValidator(unittest.TestCase):

    def test_orphan_activity_identifier(self):
        file_data = {
            'activities': [
                {'activity_identifier': 'ORG-001'},
            ],
            'transactions': [
                {'activity_identifier': 'ORG-001', 'value': '100'},
                {'activity_identifier': 'ORG-999', 'value': '200'},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        orphan_errors = [
            i for i in result.issues if i.code == ErrorCode.ORPHAN_REFERENCE
        ]
        self.assertEqual(len(orphan_errors), 1)
        self.assertIn('ORG-999', orphan_errors[0].message)

    def test_no_orphans(self):
        file_data = {
            'activities': [
                {'activity_identifier': 'ORG-001'},
            ],
            'transactions': [
                {'activity_identifier': 'ORG-001', 'value': '100'},
            ],
            'budgets': [
                {'activity_identifier': 'ORG-001', 'value': '200'},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        orphan_errors = [
            i for i in result.issues if i.code == ErrorCode.ORPHAN_REFERENCE
        ]
        self.assertEqual(len(orphan_errors), 0)

    def test_sector_percentage_sum_warning(self):
        file_data = {
            'activities': [
                {'activity_identifier': 'ORG-001'},
            ],
            'sectors': [
                {'activity_identifier': 'ORG-001', 'sector_code': '111', 'percentage': '60'},
                {'activity_identifier': 'ORG-001', 'sector_code': '222', 'percentage': '30'},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        pct_warnings = [
            i for i in result.issues if i.code == ErrorCode.PERCENTAGE_SUM
        ]
        self.assertEqual(len(pct_warnings), 1)
        self.assertIn('90', pct_warnings[0].message)

    def test_sector_percentage_sum_ok(self):
        file_data = {
            'activities': [
                {'activity_identifier': 'ORG-001'},
            ],
            'sectors': [
                {'activity_identifier': 'ORG-001', 'sector_code': '111', 'percentage': '60'},
                {'activity_identifier': 'ORG-001', 'sector_code': '222', 'percentage': '40'},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        pct_warnings = [
            i for i in result.issues if i.code == ErrorCode.PERCENTAGE_SUM
        ]
        self.assertEqual(len(pct_warnings), 0)

    def test_indicator_result_fk_error(self):
        file_data = {
            'activities': [{'activity_identifier': 'ORG-001'}],
            'results': [
                {'activity_identifier': 'ORG-001', 'result_ref': 'R1'},
            ],
            'indicators': [
                {'activity_identifier': 'ORG-001', 'result_ref': 'R1', 'indicator_ref': 'I1'},
                {'activity_identifier': 'ORG-001', 'result_ref': 'R999', 'indicator_ref': 'I2'},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        orphan_errors = [
            i for i in result.issues
            if i.code == ErrorCode.ORPHAN_REFERENCE
            and 'result_ref' in i.message
        ]
        self.assertEqual(len(orphan_errors), 1)
        self.assertIn('R999', orphan_errors[0].message)

    def test_period_indicator_fk_error(self):
        file_data = {
            'activities': [{'activity_identifier': 'ORG-001'}],
            'results': [
                {'activity_identifier': 'ORG-001', 'result_ref': 'R1'},
            ],
            'indicators': [
                {'activity_identifier': 'ORG-001', 'result_ref': 'R1', 'indicator_ref': 'I1'},
            ],
            'indicator_periods': [
                {
                    'activity_identifier': 'ORG-001',
                    'result_ref': 'R1',
                    'indicator_ref': 'I1',
                    'period_start': '2024-01-01',
                    'period_end': '2024-12-31',
                },
                {
                    'activity_identifier': 'ORG-001',
                    'result_ref': 'R1',
                    'indicator_ref': 'I999',
                    'period_start': '2024-01-01',
                    'period_end': '2024-12-31',
                },
            ],
        }
        result = CrossFileValidator().validate(file_data)
        orphan_errors = [
            i for i in result.issues
            if i.code == ErrorCode.ORPHAN_REFERENCE
            and 'indicator_ref' in i.message
        ]
        self.assertEqual(len(orphan_errors), 1)
        self.assertIn('I999', orphan_errors[0].message)

    def test_multiple_fk_tables(self):
        """Multiple child tables all checked for orphan references."""
        file_data = {
            'activities': [
                {'activity_identifier': 'ORG-001'},
            ],
            'participating_orgs': [
                {'activity_identifier': 'ORG-BAD'},
            ],
            'sectors': [
                {'activity_identifier': 'ORG-BAD2', 'percentage': ''},
            ],
        }
        result = CrossFileValidator().validate(file_data)
        orphan_errors = [
            i for i in result.issues if i.code == ErrorCode.ORPHAN_REFERENCE
        ]
        self.assertEqual(len(orphan_errors), 2)

    def test_missing_activity_dates_error(self):
        """Activity with no dates from any source triggers an error."""
        file_data = {
            'activities': [
                {
                    'activity_identifier': 'ORG-001',
                    'planned_start_date': '',
                    'actual_start_date': '',
                    'planned_end_date': '',
                    'actual_end_date': '',
                },
            ],
        }
        result = CrossFileValidator().validate(file_data)
        date_errors = [
            i for i in result.issues
            if i.code == ErrorCode.REQUIRED_FIELD
            and 'activity-date' in i.message
        ]
        self.assertEqual(len(date_errors), 1)
        self.assertIn('ORG-001', date_errors[0].message)

    def test_inline_dates_satisfy_requirement(self):
        """Activity with an inline date column should not trigger error."""
        file_data = {
            'activities': [
                {
                    'activity_identifier': 'ORG-001',
                    'planned_start_date': '2024-01-01',
                    'actual_start_date': '',
                    'planned_end_date': '',
                    'actual_end_date': '',
                },
            ],
        }
        result = CrossFileValidator().validate(file_data)
        date_errors = [
            i for i in result.issues
            if i.code == ErrorCode.REQUIRED_FIELD
            and 'activity-date' in i.message
        ]
        self.assertEqual(len(date_errors), 0)

    def test_activity_date_csv_satisfies_requirement(self):
        """Activity with a row in activity_date.csv should not trigger error."""
        file_data = {
            'activities': [
                {
                    'activity_identifier': 'ORG-001',
                    'planned_start_date': '',
                    'actual_start_date': '',
                    'planned_end_date': '',
                    'actual_end_date': '',
                },
            ],
            'activity_date': [
                {
                    'activity_identifier': 'ORG-001',
                    'iso_date': '2024-01-01',
                    'type': '1',
                },
            ],
        }
        result = CrossFileValidator().validate(file_data)
        date_errors = [
            i for i in result.issues
            if i.code == ErrorCode.REQUIRED_FIELD
            and 'activity-date' in i.message
        ]
        self.assertEqual(len(date_errors), 0)


if __name__ == '__main__':
    unittest.main()
