"""Integration tests for CsvFolderValidator using data-samples/csv_folders/."""

import csv
import tempfile
import unittest
from pathlib import Path

from okfn_iati.csv_validators.folder_validator import CsvFolderValidator
from okfn_iati.csv_validators.models import ErrorCode


class TestCsvFolderValidator(unittest.TestCase):

    def test_nonexistent_folder(self):
        result = CsvFolderValidator().validate_folder("/nonexistent/folder")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, ErrorCode.MISSING_FILE)

    def test_missing_activities_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an empty folder
            result = CsvFolderValidator().validate_folder(tmpdir)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, ErrorCode.MISSING_FILE)
            self.assertIn('activities.csv', result.errors[0].message)

    def test_minimal_valid_folder(self):
        """A folder with just activities.csv should validate (with warnings)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
            cols = IatiMultiCsvConverter.csv_files['activities']['columns']
            path = Path(tmpdir) / 'activities.csv'
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=cols)
                writer.writeheader()
                writer.writerow({
                    'activity_identifier': 'ORG-001',
                    'title': 'Test',
                    'activity_status': '2',
                    'reporting_org_ref': 'ORG',
                    'planned_start_date': '2024-01-01',
                })
            result = CsvFolderValidator().validate_folder(tmpdir)
            self.assertTrue(result.is_valid, [str(e) for e in result.errors])

    def test_real_data_sample_usaid(self):
        """Validate real CSV folder from data-samples (usaid) — should be clean."""
        folder = Path(__file__).resolve().parents[2] / 'data-samples' / 'csv_folders' / 'usaid'
        if not folder.exists():
            self.skipTest(f"Sample folder not found: {folder}")

        result = CsvFolderValidator().validate_folder(folder)
        self.assertTrue(result.is_valid, [str(e) for e in result.errors])

    def test_real_data_sample_who_arg(self):
        """Validate real CSV folder from data-samples (who_arg) — should be clean."""
        folder = Path(__file__).resolve().parents[2] / 'data-samples' / 'csv_folders' / 'who-arg'
        if not folder.exists():
            self.skipTest(f"Sample folder not found: {folder}")

        result = CsvFolderValidator().validate_folder(folder)

        # Errors expected
        self.assertFalse(result.is_valid)

        # flow_type = 20 and 35 were withdrawn from IATI codelist, causing errors like this:
        # https://iatistandard.org/en/iati-standard/203/codelists/flowtype/
        expected = [
            "column 'flow_type': Invalid value '20' for FlowType",
            "column 'flow_type': Invalid value '35' for FlowType",
        ]
        error_messages = [str(e) for e in result.errors]
        for exp in expected:
            self.assertTrue(any(exp in msg for msg in error_messages), (
                f"Expected error message not found: {exp}\n"
                f"Actual errors:\n" + "\n".join(error_messages)
            ))

    def test_real_data_sample_worldbank_679(self):
        """Validate real CSV folder from data-samples (worldbank-679) — should be clean."""
        folder = Path(__file__).resolve().parents[2] / 'data-samples' / 'csv_folders' / 'worldbank-679'
        if not folder.exists():
            self.skipTest(f"Sample folder not found: {folder}")

        result = CsvFolderValidator().validate_folder(folder)

        # Errors expected
        self.assertFalse(result.is_valid)

        expected = [
            "column 'finance_type': Invalid value '410' for FinanceType",
        ]

        error_messages = [str(e) for e in result.errors]
        for exp in expected:
            self.assertTrue(any(exp in msg for msg in error_messages), (
                f"Expected error message not found: {exp}\n"
                f"Actual errors:\n" + "\n".join(error_messages)
            ))

    def test_real_data_sample_IADB_arg(self):
        """IADB Argentina sample has human-readable values in code columns — errors expected."""
        folder = Path(__file__).resolve().parents[2] / 'data-samples' / 'csv_folders' / 'IADBArgentina'
        if not folder.exists():
            self.skipTest(f"Sample folder not found: {folder}")

        result = CsvFolderValidator().validate_folder(folder)
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) > 0)

    def test_prefix_matched_files_are_validated(self):
        """Files with org-prefix names (e.g. ORG-transactions.csv) must be
        validated and loaded for cross-file checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter

            # Write activities.csv (exact name)
            act_cols = IatiMultiCsvConverter.csv_files['activities']['columns']
            with open(Path(tmpdir) / 'activities.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=act_cols)
                writer.writeheader()
                writer.writerow({
                    'activity_identifier': 'ORG-001',
                    'title': 'Test',
                    'activity_status': '2',
                    'reporting_org_ref': 'ORG',
                })

            # Write ORG-transactions.csv (prefix name) with an orphan reference
            tx_cols = IatiMultiCsvConverter.csv_files['transactions']['columns']
            with open(Path(tmpdir) / 'ORG-transactions.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=tx_cols)
                writer.writeheader()
                writer.writerow({
                    'activity_identifier': 'ORG-ORPHAN',
                    'transaction_type': '3',
                    'transaction_date': '2024-01-01',
                    'value': '1000',
                })

            result = CsvFolderValidator().validate_folder(tmpdir)

            # The prefix-matched file must be loaded for cross-file checks
            orphan_errors = [
                e for e in result.errors
                if e.code == ErrorCode.ORPHAN_REFERENCE
                and e.value == 'ORG-ORPHAN'
            ]
            self.assertEqual(len(orphan_errors), 1, (
                "Prefix-matched file ORG-transactions.csv was not loaded "
                "for cross-file validation"
            ))

    def test_cross_file_orphan_detected(self):
        """Test that cross-file FK errors are detected in folder validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from okfn_iati.multi_csv_converter import IatiMultiCsvConverter

            # Write activities.csv
            act_cols = IatiMultiCsvConverter.csv_files['activities']['columns']
            with open(Path(tmpdir) / 'activities.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=act_cols)
                writer.writeheader()
                writer.writerow({
                    'activity_identifier': 'ORG-001',
                    'title': 'Test',
                    'activity_status': '2',
                    'reporting_org_ref': 'ORG',
                })

            # Write transactions.csv with an orphan reference
            tx_cols = IatiMultiCsvConverter.csv_files['transactions']['columns']
            with open(Path(tmpdir) / 'transactions.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=tx_cols)
                writer.writeheader()
                writer.writerow({
                    'activity_identifier': 'ORG-999',
                    'transaction_type': '3',
                    'transaction_date': '2024-01-01',
                    'value': '1000',
                })

            result = CsvFolderValidator().validate_folder(tmpdir)
            orphan_errors = [
                e for e in result.errors
                if e.code == ErrorCode.ORPHAN_REFERENCE
            ]
            self.assertTrue(len(orphan_errors) > 0)
            self.assertIn('ORG-999', orphan_errors[0].message)


if __name__ == '__main__':
    unittest.main()
