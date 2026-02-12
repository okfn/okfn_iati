"""Validator for budgets.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_date, validate_decimal, validate_enum, validate_currency
)
from okfn_iati.enums import BudgetType, BudgetStatus


class BudgetsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'budgets'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='budget_type',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, BudgetType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='budget_status',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, BudgetStatus),
                    ErrorCode.INVALID_ENUM
                )],
            ),
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
            ColumnRule(
                column='value',
                required=True,
                validators=[(validate_decimal, ErrorCode.INVALID_DECIMAL)],
            ),
            ColumnRule(
                column='currency',
                validators=[(validate_currency, ErrorCode.INVALID_CURRENCY)],
            ),
            ColumnRule(
                column='value_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
        ]
