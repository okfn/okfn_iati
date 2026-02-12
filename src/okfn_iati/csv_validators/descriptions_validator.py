"""Validator for descriptions.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_integer, validate_language


class DescriptionsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'descriptions'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='description_type',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
            ColumnRule(
                column='description_sequence',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
            ColumnRule(
                column='narrative_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='narrative_sequence',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
        ]
