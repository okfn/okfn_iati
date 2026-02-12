"""Validator for sectors.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_enum, validate_percentage, validate_url
)
from okfn_iati.enums import Sector_Vocabulary


class SectorsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'sectors'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='sector_code', required=True),
            ColumnRule(
                column='vocabulary',
                validators=[(
                    lambda v: validate_enum(v, Sector_Vocabulary),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='vocabulary_uri',
                validators=[(validate_url, ErrorCode.INVALID_URL)],
            ),
            ColumnRule(
                column='percentage',
                validators=[(validate_percentage, ErrorCode.INVALID_PERCENTAGE)],
            ),
        ]
