"""Validator for transactions.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_date, validate_decimal, validate_enum,
    validate_currency, validate_language, validate_boolean_flag
)
from okfn_iati.enums import (
    TransactionType, OrganisationType, FlowType,
    FinanceType, AidTypeVocabulary, TiedStatus,
    DisbursementChannel
)


class TransactionsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'transactions'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='transaction_type',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, TransactionType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='transaction_date',
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
            ColumnRule(
                column='description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='provider_org_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='provider_org_type',
                validators=[(
                    lambda v: validate_enum(v, OrganisationType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='receiver_org_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='receiver_org_type',
                validators=[(
                    lambda v: validate_enum(v, OrganisationType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='disbursement_channel',
                validators=[(
                    lambda v: validate_enum(v, DisbursementChannel),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='flow_type',
                validators=[(
                    lambda v: validate_enum(v, FlowType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='finance_type',
                validators=[(
                    lambda v: validate_enum(v, FinanceType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='aid_type_vocabulary',
                validators=[(
                    lambda v: validate_enum(v, AidTypeVocabulary),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='tied_status',
                validators=[(
                    lambda v: validate_enum(v, TiedStatus),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='humanitarian',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
        ]
