"""
Cross-file validation: FK integrity, percentage sums, result chains.
"""

from collections import defaultdict
from typing import Dict, List, Set

from .models import (
    CsvValidationResult, ErrorCode, ValidationIssue, ValidationLevel
)


class CrossFileValidator:
    """Validates relationships across multiple CSV files."""

    def validate(
        self,
        file_data: Dict[str, List[Dict[str, str]]]
    ) -> CsvValidationResult:
        """Run all cross-file checks.

        Args:
            file_data: Dict mapping csv_key to list of row-dicts.
                Expected keys: 'activities', 'participating_orgs', etc.
        """
        result = CsvValidationResult()

        activity_ids = self._get_activity_ids(file_data)

        # FK checks: every CSV with activity_identifier must reference activities
        fk_keys = [
            'participating_orgs', 'sectors', 'budgets', 'transactions',
            'transaction_sectors', 'locations', 'documents', 'results',
            'indicators', 'indicator_periods', 'activity_date',
            'contact_info', 'conditions', 'descriptions',
            'country_budget_items',
        ]
        for key in fk_keys:
            if key in file_data:
                self._check_fk_activity(
                    file_data[key], key, activity_ids, result
                )

        # Sector percentage sums per activity
        if 'sectors' in file_data:
            self._check_sector_percentages(file_data['sectors'], result)

        # Result -> indicator chain
        if 'results' in file_data and 'indicators' in file_data:
            self._check_indicator_result_fk(
                file_data['results'], file_data['indicators'], result
            )

        # Indicator -> indicator_periods chain
        if 'indicators' in file_data and 'indicator_periods' in file_data:
            self._check_period_indicator_fk(
                file_data['indicators'], file_data['indicator_periods'], result
            )

        return result

    @staticmethod
    def _get_activity_ids(
        file_data: Dict[str, List[Dict[str, str]]]
    ) -> Set[str]:
        """Extract all activity identifiers from activities data."""
        ids = set()
        for row in file_data.get('activities', []):
            aid = row.get('activity_identifier', '').strip()
            if aid:
                ids.add(aid)
        return ids

    @staticmethod
    def _get_filename(csv_key: str) -> str:
        from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
        cfg = IatiMultiCsvConverter.csv_files.get(csv_key, {})
        return cfg.get('filename', f'{csv_key}.csv')

    def _check_fk_activity(
        self,
        rows: List[Dict[str, str]],
        csv_key: str,
        activity_ids: Set[str],
        result: CsvValidationResult
    ) -> None:
        file_name = self._get_filename(csv_key)
        for row_idx, row in enumerate(rows, start=2):
            aid = row.get('activity_identifier', '').strip()
            if aid and aid not in activity_ids:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code=ErrorCode.ORPHAN_REFERENCE,
                    message=(
                        f"activity_identifier '{aid}' not found in activities.csv"
                    ),
                    file_name=file_name,
                    row_number=row_idx,
                    column_name='activity_identifier',
                    value=aid,
                ))

    @staticmethod
    def _check_sector_percentages(
        rows: List[Dict[str, str]],
        result: CsvValidationResult
    ) -> None:
        """Warn if sector percentages per activity don't sum to ~100."""
        sums: Dict[str, float] = defaultdict(float)
        has_pct: Dict[str, bool] = defaultdict(bool)
        for row in rows:
            aid = row.get('activity_identifier', '').strip()
            pct = row.get('percentage', '').strip()
            if aid and pct:
                try:
                    sums[aid] += float(pct)
                    has_pct[aid] = True
                except ValueError:
                    pass  # handled by per-file validators

        for aid, total in sums.items():
            if has_pct[aid] and abs(total - 100.0) > 0.01:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code=ErrorCode.PERCENTAGE_SUM,
                    message=(
                        f"Sector percentages for activity '{aid}' "
                        f"sum to {total}, expected ~100"
                    ),
                    file_name='sectors.csv',
                    column_name='percentage',
                ))

    def _check_indicator_result_fk(
        self,
        results_rows: List[Dict[str, str]],
        indicators_rows: List[Dict[str, str]],
        result: CsvValidationResult
    ) -> None:
        """Check that indicators reference existing results."""
        result_refs = set()
        for row in results_rows:
            ref = row.get('result_ref', '').strip()
            if ref:
                result_refs.add(ref)

        file_name = self._get_filename('indicators')
        for row_idx, row in enumerate(indicators_rows, start=2):
            ref = row.get('result_ref', '').strip()
            if ref and result_refs and ref not in result_refs:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code=ErrorCode.ORPHAN_REFERENCE,
                    message=(
                        f"result_ref '{ref}' not found in results.csv"
                    ),
                    file_name=file_name,
                    row_number=row_idx,
                    column_name='result_ref',
                    value=ref,
                ))

    def _check_period_indicator_fk(
        self,
        indicators_rows: List[Dict[str, str]],
        periods_rows: List[Dict[str, str]],
        result: CsvValidationResult
    ) -> None:
        """Check that indicator_periods reference existing indicators."""
        indicator_refs = set()
        for row in indicators_rows:
            ref = row.get('indicator_ref', '').strip()
            if ref:
                indicator_refs.add(ref)

        file_name = self._get_filename('indicator_periods')
        for row_idx, row in enumerate(periods_rows, start=2):
            ref = row.get('indicator_ref', '').strip()
            if ref and indicator_refs and ref not in indicator_refs:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code=ErrorCode.ORPHAN_REFERENCE,
                    message=(
                        f"indicator_ref '{ref}' not found in indicators.csv"
                    ),
                    file_name=file_name,
                    row_number=row_idx,
                    column_name='indicator_ref',
                    value=ref,
                ))
