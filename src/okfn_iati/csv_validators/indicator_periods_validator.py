"""Validator for indicator_periods.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_date


class IndicatorPeriodsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'indicator_periods'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='result_ref', required=True),
            ColumnRule(column='indicator_ref', required=True),
            ColumnRule(
                column='period_start',
                required=True,
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='period_end',
                required=True,
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
        ]
