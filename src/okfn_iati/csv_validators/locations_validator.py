"""Validator for locations.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_enum, validate_decimal, validate_language
)
from okfn_iati.enums import LocationReach, LocationID, GeographicalPrecision


class LocationsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'locations'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='location_reach',
                validators=[(
                    lambda v: validate_enum(v, LocationReach),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='location_id_vocabulary',
                validators=[(
                    lambda v: validate_enum(v, LocationID),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='name_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='activity_description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='latitude',
                validators=[(validate_decimal, ErrorCode.INVALID_DECIMAL)],
            ),
            ColumnRule(
                column='longitude',
                validators=[(validate_decimal, ErrorCode.INVALID_DECIMAL)],
            ),
            ColumnRule(
                column='exactness',
                validators=[(
                    lambda v: validate_enum(v, GeographicalPrecision),
                    ErrorCode.INVALID_ENUM
                )],
            ),
        ]
