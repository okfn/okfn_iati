"""Validator for activity_date.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_date, validate_enum, validate_language
from okfn_iati.enums import ActivityDateType


class ActivityDateCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'activity_date'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='type',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, ActivityDateType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='iso_date',
                required=True,
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='narrative_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
        ]
