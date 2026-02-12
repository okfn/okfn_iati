"""
Base CSV validator with declarative column-rule configuration.

Subclasses define ``csv_key``, ``columns_rules``, and optionally override
``validate_custom()`` for logic that cannot be expressed as column rules.
"""

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

from .models import (
    CsvValidationResult, ErrorCode, ValidationIssue, ValidationLevel
)


@dataclass
class ColumnRule:
    """Declarative validation rule for a single CSV column.

    Attributes:
        column: Column header name.
        required: If True, empty values produce an error.
        validators: List of ``(validator_fn, ErrorCode)`` pairs.
            Each validator_fn accepts a str and returns Optional[str] error message.
    """
    column: str
    required: bool = False
    validators: List[tuple] = field(default_factory=list)


class BaseCsvValidator(ABC):
    """Abstract base for per-CSV-file validators.

    Subclasses must set:
        - ``csv_key``: key into IatiMultiCsvConverter.csv_files
        - ``column_rules``: list of ColumnRule objects

    And may override:
        - ``validate_custom(rows, result)`` for row-level / multi-row logic
    """

    @property
    @abstractmethod
    def csv_key(self) -> str:
        """Key in IatiMultiCsvConverter.csv_files, e.g. 'activities'."""
        ...

    @property
    @abstractmethod
    def column_rules(self) -> List[ColumnRule]:
        """List of column rules to apply."""
        ...

    @property
    def file_name(self) -> str:
        from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
        return IatiMultiCsvConverter.csv_files[self.csv_key]['filename']

    @property
    def expected_columns(self) -> List[str]:
        from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
        return IatiMultiCsvConverter.csv_files[self.csv_key]['columns']

    def validate(self, csv_path: Union[str, Path]) -> CsvValidationResult:
        """Validate a CSV file and return structured results."""
        result = CsvValidationResult()
        csv_path = Path(csv_path)

        if not csv_path.exists():
            result.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.MISSING_FILE,
                message=f"File not found: {csv_path.name}",
                file_name=csv_path.name,
            ))
            return result

        try:
            rows = self._read_csv(csv_path)
        except Exception as e:
            result.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.CUSTOM,
                message=f"Error reading CSV: {e}",
                file_name=csv_path.name,
            ))
            return result

        if not rows:
            result.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                code=ErrorCode.EMPTY_FILE,
                message=f"File has no data rows: {csv_path.name}",
                file_name=csv_path.name,
            ))
            return result

        # Check expected columns exist
        self._check_columns(rows[0], csv_path.name, result)

        # Apply column rules to each row
        rules_map = {r.column: r for r in self.column_rules}
        for row_idx, row in enumerate(rows, start=2):  # row 1 = header
            for col, rule in rules_map.items():
                value = row.get(col, "")
                # Required check
                if rule.required and (value is None or str(value).strip() == ""):
                    result.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        code=ErrorCode.REQUIRED_FIELD,
                        message=f"Required field '{col}' is empty",
                        file_name=csv_path.name,
                        row_number=row_idx,
                        column_name=col,
                        value=value,
                    ))
                    continue  # skip further validators for missing required

                # Field validators (only if non-empty)
                if value is not None and str(value).strip() != "":
                    for validator_fn, error_code in rule.validators:
                        error_msg = validator_fn(str(value).strip())
                        if error_msg:
                            result.issues.append(ValidationIssue(
                                level=ValidationLevel.ERROR,
                                code=error_code,
                                message=error_msg,
                                file_name=csv_path.name,
                                row_number=row_idx,
                                column_name=col,
                                value=str(value).strip(),
                            ))

        # Custom validation hook
        self.validate_custom(rows, csv_path.name, result)

        return result

    def validate_custom(
        self,
        rows: List[Dict[str, str]],
        file_name: str,
        result: CsvValidationResult
    ) -> None:
        """Override for custom cross-row or multi-column logic."""
        pass

    def _check_columns(
        self,
        row: Dict[str, str],
        file_name: str,
        result: CsvValidationResult
    ) -> None:
        """Check that expected columns are present in the CSV header."""
        actual_cols = set(row.keys())
        for col in self.expected_columns:
            if col not in actual_cols:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code=ErrorCode.MISSING_COLUMN,
                    message=f"Expected column '{col}' not found",
                    file_name=file_name,
                    column_name=col,
                ))

    @staticmethod
    def _read_csv(csv_path: Path) -> List[Dict[str, str]]:
        """Read a CSV file into a list of dicts."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
