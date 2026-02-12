"""Validator for documents.csv."""

from typing import List

from .base import BaseCsvValidator, ColumnRule
from .models import ErrorCode
from .field_validators import (
    validate_url, validate_language, validate_date, validate_enum
)
from okfn_iati.enums import DocumentCategory


class DocumentsCsvValidator(BaseCsvValidator):

    @property
    def csv_key(self) -> str:
        return 'documents'

    @property
    def column_rules(self) -> List[ColumnRule]:
        return [
            ColumnRule(column='activity_identifier', required=True),
            ColumnRule(
                column='url',
                required=True,
                validators=[(validate_url, ErrorCode.INVALID_URL)],
            ),
            ColumnRule(column='format', required=True),
            ColumnRule(
                column='title_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='description_lang',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='category_code',
                validators=[(
                    lambda v: validate_enum(v, DocumentCategory),
                    ErrorCode.INVALID_ENUM
                )],
            ),
            ColumnRule(
                column='language_code',
                validators=[(validate_language, ErrorCode.INVALID_LANGUAGE)],
            ),
            ColumnRule(
                column='document_date',
                validators=[(validate_date, ErrorCode.INVALID_DATE)],
            ),
        ]
