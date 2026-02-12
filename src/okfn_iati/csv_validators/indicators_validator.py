"""Validator for indicators.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_enum, validate_boolean_flag,
    validate_integer, validate_date
)
from okfn_iati.enums import IndicatorMeasure


class IndicatorsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'indicators'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='result_ref', required=True),
            ColumnRule(
                column='indicator_measure',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, IndicatorMeasure),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='ascending',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='aggregation_status',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='baseline_year',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
            ColumnRule(
                column='baseline_iso_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
        ]
