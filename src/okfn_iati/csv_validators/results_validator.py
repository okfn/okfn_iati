"""Validator for results.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_enum, validate_boolean_flag
from okfn_iati.enums import ResultType


class ResultsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'results'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='result_type',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, ResultType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='aggregation_status',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
        ]
