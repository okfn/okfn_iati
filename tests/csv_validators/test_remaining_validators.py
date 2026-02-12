"""Grouped tests for simpler per-CSV validators."""

import csv
import os
import tempfile
import unittest

from okfn_iati.csv_validators.participating_orgs_validator import ParticipatingOrgsCsvValidator
from okfn_iati.csv_validators.locations_validator import LocationsCsvValidator
from okfn_iati.csv_validators.documents_validator import DocumentsCsvValidator
from okfn_iati.csv_validators.results_validator import ResultsCsvValidator
from okfn_iati.csv_validators.indicators_validator import IndicatorsCsvValidator
from okfn_iati.csv_validators.indicator_periods_validator import IndicatorPeriodsCsvValidator
from okfn_iati.csv_validators.activity_date_validator import ActivityDateCsvValidator
from okfn_iati.csv_validators.contact_info_validator import ContactInfoCsvValidator
from okfn_iati.csv_validators.conditions_validator import ConditionsCsvValidator
from okfn_iati.csv_validators.descriptions_validator import DescriptionsCsvValidator
from okfn_iati.csv_validators.country_budget_items_validator import CountryBudgetItemsCsvValidator
from okfn_iati.csv_validators.transaction_sectors_validator import TransactionSectorsCsvValidator
from okfn_iati.csv_validators.models import ErrorCode
from okfn_iati.multi_csv_converter import IatiMultiCsvConverter


def _write_csv(rows, csv_key):
    columns = IatiMultiCsvConverter.csv_files[csv_key]['columns']
    f = tempfile.NamedTemporaryFile(
        mode='w', suffix='.csv', delete=False, newline=''
    )
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    f.close()
    return f.name


class TestParticipatingOrgsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'role': '1',
            'org_ref': 'ORG-X',
            'org_name': 'Org X',
        }], 'participating_orgs')
        try:
            result = ParticipatingOrgsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_role(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'role': '99',
        }], 'participating_orgs')
        try:
            result = ParticipatingOrgsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        path = _write_csv([{
            'activity_identifier': '',
            'role': '',
        }], 'participating_orgs')
        try:
            result = ParticipatingOrgsCsvValidator().validate(path)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 2)
        finally:
            os.unlink(path)


class TestLocationsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'name': 'Location A',
            'latitude': '40.7128',
            'longitude': '-74.0060',
        }], 'locations')
        try:
            result = LocationsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_latitude(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'latitude': 'abc',
        }], 'locations')
        try:
            result = LocationsCsvValidator().validate(path)
            decimal_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DECIMAL
            ]
            self.assertTrue(len(decimal_errors) > 0)
        finally:
            os.unlink(path)


class TestDocumentsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'url': 'https://example.com/doc.pdf',
            'format': 'application/pdf',
            'title': 'Project Document',
        }], 'documents')
        try:
            result = DocumentsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_url(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'url': 'not-a-url',
            'format': 'application/pdf',
        }], 'documents')
        try:
            result = DocumentsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        path = _write_csv([{
            'activity_identifier': '',
            'url': '',
            'format': '',
        }], 'documents')
        try:
            result = DocumentsCsvValidator().validate(path)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 3)
        finally:
            os.unlink(path)


class TestResultsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_type': '1',
            'title': 'Result Title',
        }], 'results')
        try:
            result = ResultsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_result_type(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_type': '99',
        }], 'results')
        try:
            result = ResultsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)


class TestIndicatorsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_ref': 'R1',
            'indicator_measure': '1',
            'title': 'Indicator',
        }], 'indicators')
        try:
            result = IndicatorsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_measure(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_ref': 'R1',
            'indicator_measure': '99',
        }], 'indicators')
        try:
            result = IndicatorsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)


class TestIndicatorPeriodsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_ref': 'R1',
            'indicator_ref': 'I1',
            'period_start': '2024-01-01',
            'period_end': '2024-12-31',
        }], 'indicator_periods')
        try:
            result = IndicatorPeriodsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_dates(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'result_ref': 'R1',
            'indicator_ref': 'I1',
            'period_start': 'bad',
            'period_end': 'bad',
        }], 'indicator_periods')
        try:
            result = IndicatorPeriodsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
            date_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_DATE
            ]
            self.assertEqual(len(date_errors), 2)
        finally:
            os.unlink(path)


class TestActivityDateValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'type': '1',
            'iso_date': '2024-01-01',
        }], 'activity_date')
        try:
            result = ActivityDateCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_type(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'type': '99',
            'iso_date': '2024-01-01',
        }], 'activity_date')
        try:
            result = ActivityDateCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)


class TestContactInfoValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'contact_type': '1',
            'organisation': 'Org Name',
            'email': 'test@example.com',
        }], 'contact_info')
        try:
            result = ContactInfoCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)


class TestConditionsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'condition_type': '1',
            'condition_text': 'Some condition',
        }], 'conditions')
        try:
            result = ConditionsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_type(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'condition_type': '99',
        }], 'conditions')
        try:
            result = ConditionsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)


class TestDescriptionsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'description_type': '1',
            'narrative': 'Text',
        }], 'descriptions')
        try:
            result = DescriptionsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_sequence(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'description_sequence': 'abc',
        }], 'descriptions')
        try:
            result = DescriptionsCsvValidator().validate(path)
            int_errors = [
                e for e in result.errors if e.code == ErrorCode.INVALID_INTEGER
            ]
            self.assertTrue(len(int_errors) > 0)
        finally:
            os.unlink(path)


class TestCountryBudgetItemsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'vocabulary': '1',
            'budget_item_code': '1.1.1',
            'budget_item_percentage': '100',
        }], 'country_budget_items')
        try:
            result = CountryBudgetItemsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_invalid_percentage(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'vocabulary': '1',
            'budget_item_code': '1.1.1',
            'budget_item_percentage': '200',
        }], 'country_budget_items')
        try:
            result = CountryBudgetItemsCsvValidator().validate(path)
            self.assertFalse(result.is_valid)
        finally:
            os.unlink(path)


class TestTransactionSectorsValidator(unittest.TestCase):

    def test_valid(self):
        path = _write_csv([{
            'activity_identifier': 'ORG-001',
            'sector_code': '11110',
            'vocabulary': '1',
        }], 'transaction_sectors')
        try:
            result = TransactionSectorsCsvValidator().validate(path)
            self.assertTrue(result.is_valid, result.errors)
        finally:
            os.unlink(path)

    def test_missing_required(self):
        path = _write_csv([{
            'activity_identifier': '',
            'sector_code': '',
        }], 'transaction_sectors')
        try:
            result = TransactionSectorsCsvValidator().validate(path)
            req_errors = [
                e for e in result.errors if e.code == ErrorCode.REQUIRED_FIELD
            ]
            self.assertEqual(len(req_errors), 2)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
