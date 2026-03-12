"""
IATI organisation CSV to XML builders.

Functions for building IATI organisation model objects from CSV row data.
"""

from typing import Dict, Any

# Import dataclasses from parent module - will need to be available
# These are re-exported from base.py


def build_organisation_budget(budget_data: Dict[str, str]) -> Dict[str, Any]:
    """Build budget dictionary from CSV data."""
    budget = {
        'kind': budget_data.get('budget_kind', 'total-budget'),
        'status': budget_data.get('budget_status'),
        'period_start': budget_data.get('period_start'),
        'period_end': budget_data.get('period_end'),
        'value': budget_data.get('value'),
        'currency': budget_data.get('currency', 'USD'),
        'value_date': budget_data.get('value_date'),
        'recipient_org_ref': budget_data.get('recipient_org_ref'),
        'recipient_org_type': budget_data.get('recipient_org_type'),
        'recipient_org_name': budget_data.get('recipient_org_name'),
        'recipient_country_code': budget_data.get('recipient_country_code'),
        'recipient_region_code': budget_data.get('recipient_region_code'),
        'recipient_region_vocabulary': budget_data.get('recipient_region_vocabulary')
    }
    return budget


def build_organisation_expenditure(exp_data: Dict[str, str]) -> Dict[str, Any]:
    """Build expenditure dictionary from CSV data."""
    expenditure = {
        'period_start': exp_data.get('period_start'),
        'period_end': exp_data.get('period_end'),
        'value': exp_data.get('value'),
        'currency': exp_data.get('currency', 'USD'),
        'value_date': exp_data.get('value_date')
    }
    return expenditure


def build_organisation_document(doc_data: Dict[str, str]) -> Dict[str, Any]:
    """Build document dictionary from CSV data."""
    document = {
        'url': doc_data.get('url', ''),
        'format': doc_data.get('format', 'text/html'),
        'title': doc_data.get('title'),
        'category_code': doc_data.get('category_code'),
        'language': doc_data.get('language'),
        'document_date': doc_data.get('document_date')
    }
    return document
