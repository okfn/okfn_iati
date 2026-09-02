"""Validator for locations.csv."""

from typing import Dict, List, Optional

from .base import BaseCsvValidator, ColumnRule
from .models import CsvValidationResult, ErrorCode, ValidationIssue, ValidationLevel
from .field_validators import (
    validate_enum, validate_decimal, validate_integer, validate_language
)
from okfn_iati.enums import (
    LocationReach, LocationID, GeographicExactness, GeographicLocationClass, LocationType
)


def validate_feature_designation(value: str) -> Optional[str]:
    """Validate against the LocationType codelist without dumping ~700 codes."""
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    # LocationType is built from a CSV: member names are the codes (PPL, ADM1...)
    if value not in LocationType.__members__:
        return (
            f"Invalid value '{value}' for LocationType (feature_designation). "
            "See https://iatistandard.org/en/iati-standard/203/codelists/locationtype/"
        )
    return None


def validate_latitude(value: str) -> Optional[str]:
    err = validate_decimal(value)
    if err:
        return err
    if not -90 <= float(value) <= 90:
        return f"Latitude '{value}' out of range [-90, 90]"
    return None


def validate_longitude(value: str) -> Optional[str]:
    err = validate_decimal(value)
    if err:
        return err
    if not -180 <= float(value) <= 180:
        return f"Longitude '{value}' out of range [-180, 180]"
    return None


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
                validators=[(validate_latitude, ErrorCode.INVALID_DECIMAL)],
            ),
            ColumnRule(
                column='longitude',
                validators=[(validate_longitude, ErrorCode.INVALID_DECIMAL)],
            ),
            ColumnRule(
                column='exactness',
                validators=[(
                    lambda v: validate_enum(v, GeographicExactness),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='location_class',
                validators=[(
                    lambda v: validate_enum(v, GeographicLocationClass),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='feature_designation',
                validators=[(validate_feature_designation, ErrorCode.INVALID_ENUM)],
            ),
            ColumnRule(
                column='administrative_vocabulary',
                validators=[(
                    lambda v: validate_enum(v, LocationID),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='administrative_level',
                validators=[(validate_integer, ErrorCode.INVALID_INTEGER)],
            ),
        ]

    # Column pairs that only make sense together (IATI 2.03 requires both attributes)
    PAIRED_COLUMNS = (
        ('latitude', 'longitude', "<point><pos> needs both latitude and longitude"),
        ('location_id_vocabulary', 'location_id_code', "<location-id> needs both vocabulary and code"),
        ('administrative_vocabulary', 'administrative_code', "<administrative> needs both vocabulary and code"),
    )

    def validate_custom(
        self,
        rows: List[Dict[str, str]],
        file_name: str,
        result: CsvValidationResult
    ) -> None:
        for row_idx, row in enumerate(rows, start=2):
            for col_a, col_b, why in self.PAIRED_COLUMNS:
                a = (row.get(col_a) or '').strip()
                b = (row.get(col_b) or '').strip()
                if bool(a) != bool(b):
                    missing = col_b if a else col_a
                    result.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        code=ErrorCode.CUSTOM,
                        message=f"'{missing}' is empty but '{col_a if missing == col_b else col_b}' is set: {why}",
                        file_name=file_name,
                        row_number=row_idx,
                        column_name=missing,
                    ))

            if (row.get('administrative_country') or '').strip():
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code=ErrorCode.CUSTOM,
                    message=(
                        "'administrative_country' is not part of IATI 2.03 and is ignored; "
                        "use location_id_vocabulary=A4 with the ISO country code instead"
                    ),
                    file_name=file_name,
                    row_number=row_idx,
                    column_name='administrative_country',
                    value=row.get('administrative_country'),
                ))

            has_content = any((row.get(c) or '').strip() for c in (
                'name', 'latitude', 'location_id_code', 'administrative_code'
            ))
            if not has_content:
                result.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code=ErrorCode.CUSTOM,
                    message="Location has no name, coordinates, location_id_code or administrative_code",
                    file_name=file_name,
                    row_number=row_idx,
                ))
