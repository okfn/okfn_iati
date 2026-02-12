"""Validator for contact_info.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_enum, validate_language, validate_url,
    validate_boolean_flag
)
from okfn_iati.enums import ContactType


class ContactInfoCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'contact_info'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='contact_type',
                validators=[(
                    lambda v: validate_enum(v, ContactType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='organisation_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='department_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='person_name_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='person_name_present',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='job_title_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='email_present',
                validators=[(validate_boolean_flag, ErrorCode.INVALID_BOOLEAN)],
            ),
            ColumnRule(
                column='website',
                validators=[(validate_url, ErrorCode.INVALID_URL)],
            ),
            ColumnRule(
                column='mailing_address_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
        ]
