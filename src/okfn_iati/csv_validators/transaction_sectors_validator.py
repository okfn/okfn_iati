"""Validator for transaction_sectors.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_enum, validate_url
from okfn_iati.enums import TransactionType, Sector_Vocabulary


class TransactionSectorsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'transaction_sectors'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='sector_code', required=True),
            ColumnRule(
                column='transaction_type',
                validators=[(
                    lambda v: validate_enum(v, TransactionType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
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
        ]
