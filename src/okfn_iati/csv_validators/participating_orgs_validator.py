"""Validator for participating_orgs.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_enum, validate_crs_code, validate_language
)
from okfn_iati.enums import OrganisationType, OrganisationRole


class ParticipatingOrgsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'participating_orgs'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='role',
                required=True,
                validators=[(
                    lambda v: validate_enum(v, OrganisationRole),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='org_type',
                validators=[(
                    lambda v: validate_enum(v, OrganisationType),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='org_name_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='crs_channel_code',
                validators=[(validate_crs_code, ErrorCode.INVALID_CRS_CODE)],
            ),
        ]
