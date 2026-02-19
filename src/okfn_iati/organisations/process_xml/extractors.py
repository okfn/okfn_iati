"""
IATI organisation XML to CSV extractors.

Functions for extracting organisation data from XML elements into CSV row dictionaries.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict


def extract_organisation_basic_info(org_elem: ET.Element) -> Dict[str, str]:
    """Extract basic organisation information."""
    data = {}

    # Organisation identifier
    org_id_elem = org_elem.find('organisation-identifier')
    data['organisation_identifier'] = org_id_elem.text if org_id_elem is not None else ''

    # Name
    name_elem = org_elem.find('name/narrative')
    data['name'] = name_elem.text if name_elem is not None else ''

    # Reporting org
    rep_org_elem = org_elem.find('reporting-org')
    if rep_org_elem is not None:
        data['reporting_org_ref'] = rep_org_elem.get('ref', '')
        data['reporting_org_type'] = rep_org_elem.get('type', '')

        rep_org_name = rep_org_elem.find('narrative')
        data['reporting_org_name'] = rep_org_name.text if rep_org_name is not None else ''
        # Preserve language attribute from reporting org narrative
        data['reporting_org_lang'] = rep_org_name.get(
            '{http://www.w3.org/XML/1998/namespace}lang', ''
        ) if rep_org_name is not None else ''

    # Default currency
    data['default_currency'] = org_elem.get('default-currency', 'USD')

    # Preserve xml:lang from the organisation element
    data['xml_lang'] = org_elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')

    return data


def extract_organisation_names(org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
    """Extract organisation names in multiple languages."""
    names = []

    name_elem = org_elem.find('name')
    if name_elem is not None:
        narratives = name_elem.findall('narrative')
        for narr in narratives:
            names.append({
                'organisation_identifier': org_identifier,
                'language': narr.get('{http://www.w3.org/XML/1998/namespace}lang', ''),
                'name': narr.text if narr.text else ''
            })

    return names


def extract_organisation_budgets(org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
    """Extract budget information."""
    budgets = []

    # Total budgets
    for budget_elem in org_elem.findall('total-budget'):
        budget_data = {
            'organisation_identifier': org_identifier,
            'budget_kind': 'total-budget',
            'budget_status': budget_elem.get('status', '1'),
            'period_start': '',
            'period_end': '',
            'value': '',
            'currency': '',
            'value_date': '',
            'recipient_org_ref': '',
            'recipient_org_type': '',
            'recipient_org_name': '',
            'recipient_country_code': '',
            'recipient_region_code': '',
            'recipient_region_vocabulary': ''
        }

        period_start = budget_elem.find('period-start')
        if period_start is not None:
            budget_data['period_start'] = period_start.get('iso-date', '')

        period_end = budget_elem.find('period-end')
        if period_end is not None:
            budget_data['period_end'] = period_end.get('iso-date', '')

        value_elem = budget_elem.find('value')
        if value_elem is not None:
            budget_data['value'] = value_elem.text if value_elem.text else ''
            budget_data['currency'] = value_elem.get('currency', '')
            budget_data['value_date'] = value_elem.get('value-date', '')

        budgets.append(budget_data)

    # Recipient org budgets
    for budget_elem in org_elem.findall('recipient-org-budget'):
        budget_data = {
            'organisation_identifier': org_identifier,
            'budget_kind': 'recipient-org-budget',
            'budget_status': budget_elem.get('status', '1'),
            'period_start': '',
            'period_end': '',
            'value': '',
            'currency': '',
            'value_date': '',
            'recipient_org_ref': '',
            'recipient_org_type': '',
            'recipient_org_name': '',
            'recipient_country_code': '',
            'recipient_region_code': '',
            'recipient_region_vocabulary': ''
        }

        recip_org = budget_elem.find('recipient-org')
        if recip_org is not None:
            budget_data['recipient_org_ref'] = recip_org.get('ref', '')
            budget_data['recipient_org_type'] = recip_org.get('type', '')
            recip_org_name = recip_org.find('narrative')
            budget_data['recipient_org_name'] = recip_org_name.text if recip_org_name is not None else ''

        period_start = budget_elem.find('period-start')
        if period_start is not None:
            budget_data['period_start'] = period_start.get('iso-date', '')

        period_end = budget_elem.find('period-end')
        if period_end is not None:
            budget_data['period_end'] = period_end.get('iso-date', '')

        value_elem = budget_elem.find('value')
        if value_elem is not None:
            budget_data['value'] = value_elem.text if value_elem.text else ''
            budget_data['currency'] = value_elem.get('currency', '')
            budget_data['value_date'] = value_elem.get('value-date', '')

        budgets.append(budget_data)

    # Recipient country budgets
    for budget_elem in org_elem.findall('recipient-country-budget'):
        budget_data = {
            'organisation_identifier': org_identifier,
            'budget_kind': 'recipient-country-budget',
            'budget_status': budget_elem.get('status', '1'),
            'period_start': '',
            'period_end': '',
            'value': '',
            'currency': '',
            'value_date': '',
            'recipient_org_ref': '',
            'recipient_org_type': '',
            'recipient_org_name': '',
            'recipient_country_code': '',
            'recipient_region_code': '',
            'recipient_region_vocabulary': ''
        }

        recip_country = budget_elem.find('recipient-country')
        if recip_country is not None:
            budget_data['recipient_country_code'] = recip_country.get('code', '')

        period_start = budget_elem.find('period-start')
        if period_start is not None:
            budget_data['period_start'] = period_start.get('iso-date', '')

        period_end = budget_elem.find('period-end')
        if period_end is not None:
            budget_data['period_end'] = period_end.get('iso-date', '')

        value_elem = budget_elem.find('value')
        if value_elem is not None:
            budget_data['value'] = value_elem.text if value_elem.text else ''
            budget_data['currency'] = value_elem.get('currency', '')
            budget_data['value_date'] = value_elem.get('value-date', '')

        budgets.append(budget_data)

    # Recipient region budgets
    for budget_elem in org_elem.findall('recipient-region-budget'):
        budget_data = {
            'organisation_identifier': org_identifier,
            'budget_kind': 'recipient-region-budget',
            'budget_status': budget_elem.get('status', '1'),
            'period_start': '',
            'period_end': '',
            'value': '',
            'currency': '',
            'value_date': '',
            'recipient_org_ref': '',
            'recipient_org_type': '',
            'recipient_org_name': '',
            'recipient_country_code': '',
            'recipient_region_code': '',
            'recipient_region_vocabulary': ''
        }

        recip_region = budget_elem.find('recipient-region')
        if recip_region is not None:
            budget_data['recipient_region_code'] = recip_region.get('code', '')
            budget_data['recipient_region_vocabulary'] = recip_region.get('vocabulary', '1')

        period_start = budget_elem.find('period-start')
        if period_start is not None:
            budget_data['period_start'] = period_start.get('iso-date', '')

        period_end = budget_elem.find('period-end')
        if period_end is not None:
            budget_data['period_end'] = period_end.get('iso-date', '')

        value_elem = budget_elem.find('value')
        if value_elem is not None:
            budget_data['value'] = value_elem.text if value_elem.text else ''
            budget_data['currency'] = value_elem.get('currency', '')
            budget_data['value_date'] = value_elem.get('value-date', '')

        budgets.append(budget_data)

    return budgets


def extract_organisation_expenditures(org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
    """Extract expenditure information."""
    expenditures = []

    for exp_elem in org_elem.findall('total-expenditure'):
        exp_data = {
            'organisation_identifier': org_identifier,
            'period_start': '',
            'period_end': '',
            'value': '',
            'currency': '',
            'value_date': ''
        }

        period_start = exp_elem.find('period-start')
        if period_start is not None:
            exp_data['period_start'] = period_start.get('iso-date', '')

        period_end = exp_elem.find('period-end')
        if period_end is not None:
            exp_data['period_end'] = period_end.get('iso-date', '')

        value_elem = exp_elem.find('value')
        if value_elem is not None:
            exp_data['value'] = value_elem.text if value_elem.text else ''
            exp_data['currency'] = value_elem.get('currency', '')
            exp_data['value_date'] = value_elem.get('value-date', '')

        expenditures.append(exp_data)

    return expenditures


def extract_organisation_documents(org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
    """Extract document information."""
    documents = []

    for doc_elem in org_elem.findall('document-link'):
        doc_data = {
            'organisation_identifier': org_identifier,
            'url': doc_elem.get('url', ''),
            'format': doc_elem.get('format', ''),
            'title': '',
            'category_code': '',
            'language': '',
            'document_date': ''
        }

        title_elem = doc_elem.find('title/narrative')
        if title_elem is not None:
            doc_data['title'] = title_elem.text if title_elem.text else ''

        category = doc_elem.find('category')
        if category is not None:
            doc_data['category_code'] = category.get('code', '')

        language = doc_elem.find('language')
        if language is not None:
            doc_data['language'] = language.get('code', '')

        doc_date = doc_elem.find('document-date')
        if doc_date is not None:
            doc_data['document_date'] = doc_date.get('iso-date', '')

        documents.append(doc_data)

    return documents
