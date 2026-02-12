"""Validator for country_budget_items.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import validate_percentage, validate_language


class CountryBudgetItemsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'country_budget_items'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(column='vocabulary', required=True),
            ColumnRule(column='budget_item_code', required=True),
            ColumnRule(
                column='budget_item_percentage',
                validators=[(validate_percentage, ErrorCode.INVALID_PERCENTAGE)],
            ),
            ColumnRule(
                column='description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
        ]
