"""
Data models for CSV validation results.

Provides structured types for reporting validation issues with
row/column-level detail.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ValidationLevel(Enum):
    """Severity level of a validation issue."""
    ERROR = "error"
    WARNING = "warning"


class ErrorCode(Enum):
    """Categorized error codes for CSV validation issues."""
    # Field-level errors
    REQUIRED_FIELD = "required_field"
    INVALID_DATE = "invalid_date"
    INVALID_DATETIME = "invalid_datetime"
    INVALID_INTEGER = "invalid_integer"
    INVALID_DECIMAL = "invalid_decimal"
    INVALID_ENUM = "invalid_enum"
    INVALID_PERCENTAGE = "invalid_percentage"
    INVALID_BOOLEAN = "invalid_boolean"
    INVALID_URL = "invalid_url"
    INVALID_CURRENCY = "invalid_currency"
    INVALID_LANGUAGE = "invalid_language"
    INVALID_CRS_CODE = "invalid_crs_code"

    # Structural errors
    MISSING_COLUMN = "missing_column"
    MISSING_FILE = "missing_file"
    EMPTY_FILE = "empty_file"
    DUPLICATE_ROW = "duplicate_row"

    # Cross-file errors
    ORPHAN_REFERENCE = "orphan_reference"
    PERCENTAGE_SUM = "percentage_sum"

    # Custom validation errors
    CUSTOM = "custom"


@dataclass
class ValidationIssue:
    """A single validation issue found during CSV validation.

    Attributes:
        level: Severity of the issue (error or warning).
        code: Categorized error code.
        message: Human-readable description of the problem.
        file_name: Name of the CSV file where the issue was found.
        row_number: 1-based row number in the CSV (header is row 1).
        column_name: Column name where the issue was found.
        value: The problematic value (if applicable).
    """
    level: ValidationLevel
    code: ErrorCode
    message: str
    file_name: Optional[str] = None
    row_number: Optional[int] = None
    column_name: Optional[str] = None
    value: Optional[str] = None

    def __str__(self):
        parts = []
        if self.file_name:
            parts.append(self.file_name)
        if self.row_number is not None:
            parts.append(f"row {self.row_number}")
        if self.column_name:
            parts.append(f"column '{self.column_name}'")
        location = ", ".join(parts)
        prefix = f"[{self.level.value.upper()}]"
        if location:
            return f"{prefix} {location}: {self.message}"
        return f"{prefix} {self.message}"


@dataclass
class CsvValidationResult:
    """Aggregated result of CSV validation.

    Attributes:
        issues: All validation issues found.
    """
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if there are no error-level issues."""
        return not any(
            i.level == ValidationLevel.ERROR for i in self.issues
        )

    @property
    def errors(self) -> List[ValidationIssue]:
        """All error-level issues."""
        return [
            i for i in self.issues if i.level == ValidationLevel.ERROR
        ]

    @property
    def warnings(self) -> List[ValidationIssue]:
        """All warning-level issues."""
        return [
            i for i in self.issues if i.level == ValidationLevel.WARNING
        ]

    def merge(self, other: 'CsvValidationResult') -> None:
        """Merge issues from another result into this one."""
        self.issues.extend(other.issues)
