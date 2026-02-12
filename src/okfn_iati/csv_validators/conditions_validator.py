"""Validator for conditions.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_enum
from okfn_iati.enums import ConditionType


class ConditionsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'conditions'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='condition_type',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, ConditionType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
        ]
