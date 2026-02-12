"""Tests for csv_validators.models."""

import unittest

from okfn_iati.csv_validators.models import (
    ValidationLevel, ErrorCode, ValidationIssue, CsvValidationResult
)


class TestValidationIssue(unittest.TestCase):

    def test_str_full(self):
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            code=ErrorCode.REQUIRED_FIELD,
            message="Value is required",
            file_name="activities.csv",
            row_number=3,
            column_name="title",
            value=""
        )
        result = str(issue)
        self.assertIn("[ERROR]", result)
        self.assertIn("activities.csv", result)
        self.assertIn("row 3", result)
        self.assertIn("column 'title'", result)
        self.assertIn("Value is required", result)

    def test_str_minimal(self):
        issue = ValidationIssue(
            level=ValidationLevel.WARNING,
            code=ErrorCode.PERCENTAGE_SUM,
            message="Sectors do not sum to 100%"
        )
        result = str(issue)
        self.assertIn("[WARNING]", result)
        self.assertIn("Sectors do not sum to 100%", result)

    def test_str_partial_location(self):
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            code=ErrorCode.MISSING_FILE,
            message="File not found",
            file_name="budgets.csv"
        )
        result = str(issue)
        self.assertIn("budgets.csv", result)


class TestCsvValidationResult(unittest.TestCase):

    def test_empty_is_valid(self):
        result = CsvValidationResult()
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_warnings_only_is_valid(self):
        result = CsvValidationResult(issues=[
            ValidationIssue(
                level=ValidationLevel.WARNING,
                code=ErrorCode.PERCENTAGE_SUM,
                message="Sum is 99%"
            )
        ])
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(len(result.errors), 0)

    def test_error_makes_invalid(self):
        result = CsvValidationResult(issues=[
            ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.REQUIRED_FIELD,
                message="Missing"
            )
        ])
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)

    def test_merge(self):
        r1 = CsvValidationResult(issues=[
            ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.REQUIRED_FIELD,
                message="err1"
            )
        ])
        r2 = CsvValidationResult(issues=[
            ValidationIssue(
                level=ValidationLevel.WARNING,
                code=ErrorCode.PERCENTAGE_SUM,
                message="warn1"
            ),
            ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.INVALID_DATE,
                message="err2"
            )
        ])
        r1.merge(r2)
        self.assertEqual(len(r1.issues), 3)
        self.assertEqual(len(r1.errors), 2)
        self.assertEqual(len(r1.warnings), 1)

    def test_mixed_errors_and_warnings(self):
        result = CsvValidationResult(issues=[
            ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.REQUIRED_FIELD,
                message="err"
            ),
            ValidationIssue(
                level=ValidationLevel.WARNING,
                code=ErrorCode.PERCENTAGE_SUM,
                message="warn"
            ),
        ])
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.warnings), 1)


if __name__ == '__main__':
    unittest.main()
