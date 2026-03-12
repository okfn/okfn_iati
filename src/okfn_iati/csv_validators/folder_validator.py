"""
CsvFolderValidator — orchestrator that validates a complete CSV folder.

Runs per-file validators on each present CSV, then cross-file checks.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Union

from .models import (
    CsvValidationResult, ErrorCode, ValidationIssue, ValidationLevel
)
from .cross_file_validator import CrossFileValidator
from .activities_validator import ActivitiesCsvValidator
from .participating_orgs_validator import ParticipatingOrgsCsvValidator
from .sectors_validator import SectorsCsvValidator
from .budgets_validator import BudgetsCsvValidator
from .transactions_validator import TransactionsCsvValidator
from .transaction_sectors_validator import TransactionSectorsCsvValidator
from .locations_validator import LocationsCsvValidator
from .documents_validator import DocumentsCsvValidator
from .results_validator import ResultsCsvValidator
from .indicators_validator import IndicatorsCsvValidator
from .indicator_periods_validator import IndicatorPeriodsCsvValidator
from .activity_date_validator import ActivityDateCsvValidator
from .contact_info_validator import ContactInfoCsvValidator
from .conditions_validator import ConditionsCsvValidator
from .descriptions_validator import DescriptionsCsvValidator
from .country_budget_items_validator import CountryBudgetItemsCsvValidator


# Maps csv_key -> validator class
_VALIDATORS = {
    'activities': ActivitiesCsvValidator,
    'participating_orgs': ParticipatingOrgsCsvValidator,
    'sectors': SectorsCsvValidator,
    'budgets': BudgetsCsvValidator,
    'transactions': TransactionsCsvValidator,
    'transaction_sectors': TransactionSectorsCsvValidator,
    'locations': LocationsCsvValidator,
    'documents': DocumentsCsvValidator,
    'results': ResultsCsvValidator,
    'indicators': IndicatorsCsvValidator,
    'indicator_periods': IndicatorPeriodsCsvValidator,
    'activity_date': ActivityDateCsvValidator,
    'contact_info': ContactInfoCsvValidator,
    'conditions': ConditionsCsvValidator,
    'descriptions': DescriptionsCsvValidator,
    'country_budget_items': CountryBudgetItemsCsvValidator,
}


class CsvFolderValidator:
    """Validate a complete CSV folder for IATI activity data.

    Usage::

        result = CsvFolderValidator().validate_folder("./my_data")
        if not result.is_valid:
            for error in result.errors:
                print(error)
    """

    def validate_folder(
        self, folder_path: Union[str, Path]
    ) -> CsvValidationResult:
        """Validate all CSV files in a folder.

        Args:
            folder_path: Path to the folder containing CSV files.

        Returns:
            Aggregated validation result.
        """
        from okfn_iati.activities import IatiMultiCsvConverter

        folder = Path(folder_path)
        result = CsvValidationResult()

        if not folder.is_dir():
            result.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.MISSING_FILE,
                message=f"Folder not found: {folder}",
            ))
            return result

        # Check required file (activities.csv) exists
        activities_file = folder / 'activities.csv'
        if not activities_file.exists():
            result.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                code=ErrorCode.MISSING_FILE,
                message="Required file activities.csv not found",
                file_name='activities.csv',
            ))
            return result

        # Run per-file validators on each present CSV
        file_data: Dict[str, List[Dict[str, str]]] = {}
        csv_files = IatiMultiCsvConverter.csv_files

        for csv_key, cfg in csv_files.items():
            filename = cfg['filename']
            csv_path = folder / filename
            if not csv_path.exists():
                # Try finding the file with a prefix pattern
                # (some folders use ORG-filename.csv patterns)
                matching = self._find_csv_file(folder, filename)
                if matching:
                    csv_path = matching
                else:
                    if cfg.get('required', False):
                        result.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            code=ErrorCode.MISSING_FILE,
                            message=f"Required file {filename} not found",
                            file_name=filename,
                        ))
                    continue

            # Validate the file
            if csv_key in _VALIDATORS:
                validator = _VALIDATORS[csv_key]()
                file_result = validator.validate(csv_path)
                result.merge(file_result)

            # Read the data for cross-file validation
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_data[csv_key] = list(reader)
            except Exception:
                pass  # already reported by per-file validator

        # Run cross-file validation
        if file_data.get('activities'):
            cross_result = CrossFileValidator().validate(file_data)
            result.merge(cross_result)

        return result

    @staticmethod
    def _find_csv_file(folder: Path, filename: str) -> Optional[Path]:
        """Find a CSV file that may have a prefix (e.g. ORG-filename.csv)."""
        stem = Path(filename).stem  # e.g., 'participating_orgs'
        for f in folder.iterdir():
            if f.is_file() and f.suffix == '.csv' and stem in f.stem:
                return f
        return None
