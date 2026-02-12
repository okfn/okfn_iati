"""Validator for activities.csv — the core CSV file."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_date, validate_datetime_iso, validate_enum,
    validate_boolean_flag, validate_currency, validate_language,
    validate_integer, validate_percentage
)
from okfn_iati.enums import (
    ActivityStatus, ActivityScope, OrganisationType,
    OrganisationRole, CollaborationType, FlowType,
    FinanceType, AidTypeVocabulary, TiedStatus
)


class ActivitiesCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'activities'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(
                column='activity_identifier',
                required=True,
            ),
            ColumnRule(
                column='title',
                required=True,
            ),
            ColumnRule(
                column='title_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='activity_status',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, ActivityStatus),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='activity_scope',
                validators=[(
                    lambda v: validate_enum(v, ActivityScope),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='default_currency',
                validators=[(validate_currency, ErrorCode.INVALID_CURRENCY)],
            ),
            ColumnRule(
                column='humanitarian',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='hierarchy',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
            ColumnRule(
                column='last_updated_datetime',
                validators=[(validate_datetime_iso, ErrorCode.INVALID_DATETIME)],
            ),
            ColumnRule(
                column='xml_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='reporting_org_ref',
                required=True,
            ),
            ColumnRule(
                column='reporting_org_name_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='reporting_org_type',
                validators=[(
                    lambda v: validate_enum(v, OrganisationType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='reporting_org_role',
                validators=[(
                    lambda v: validate_enum(v, OrganisationRole),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='reporting_org_secondary_reporter',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='planned_start_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='actual_start_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='planned_end_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='actual_end_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
            ColumnRule(
                column='recipient_country_percentage',
                validators=[(validate_percentage, ErrorCode.INVALID_PERCENTAGE)],
            ),
            ColumnRule(
                column='recipient_country_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='recipient_region_percentage',
                validators=[(validate_percentage, ErrorCode.INVALID_PERCENTAGE)],
            ),
            ColumnRule(
                column='recipient_region_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='collaboration_type',
                validators=[(
                    lambda v: validate_enum(v, CollaborationType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='default_flow_type',
                validators=[(
                    lambda v: validate_enum(v, FlowType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='default_finance_type',
                validators=[(
                    lambda v: validate_enum(v, FinanceType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='default_aid_type_vocabulary',
                validators=[(
                    lambda v: validate_enum(v, AidTypeVocabulary),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='default_tied_status',
                validators=[(
                    lambda v: validate_enum(v, TiedStatus),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='conditions_attached',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
        ]
