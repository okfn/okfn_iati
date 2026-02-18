"""
IATI XML to CSV extractors module.

This module contains all functions for extracting IATI data from XML elements
into CSV row dictionaries.
"""

import xml.etree.ElementTree as ET
import html
from typing import List, Dict, Optional


def get_text_content(element: Optional[ET.Element]) -> str:
    """Get text content from element, unescaping HTML entities."""
    if element is None or not element.text:
        return ''
    return html.unescape(element.text)


def get_activity_identifier(activity_elem: ET.Element) -> str:
    """Get activity identifier from XML element."""
    id_elem = activity_elem.find('iati-identifier')
    return get_text_content(id_elem)


def extract_description_data(
    desc_elem: ET.Element,
    activity_id: str,
    description_index: int,
    narrative_elem: Optional[ET.Element],
    narrative_index: int
) -> Dict[str, str]:
    """Extract a single description narrative row."""
    data = {
        'activity_identifier': activity_id,
        'description_type': desc_elem.get('type', ''),
        'description_sequence': str(description_index),
        'narrative_sequence': str(narrative_index)
    }

    if narrative_elem is not None:
        data['narrative'] = get_text_content(narrative_elem)
        data['narrative_lang'] = narrative_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
    else:
        data['narrative'] = ''
        data['narrative_lang'] = ''

    return data


def extract_indicator_period_data(
    period_elem: ET.Element,
    activity_id: str,
    result_ref: str,
    indicator_ref: str
) -> Dict[str, str]:
    """Extract indicator period data."""
    data = {
        'activity_identifier': activity_id,
        'result_ref': result_ref,
        'indicator_ref': indicator_ref
    }

    # Period dates
    period_start = period_elem.find('period-start')
    data['period_start'] = period_start.get('iso-date') if period_start is not None else ''

    period_end = period_elem.find('period-end')
    data['period_end'] = period_end.get('iso-date') if period_end is not None else ''

    # Target
    target_elem = period_elem.find('target')
    if target_elem is not None:
        data['target_value'] = target_elem.get('value', '')
        target_comment = target_elem.find('comment/narrative')
        data['target_comment'] = get_text_content(target_comment)
    else:
        data['target_value'] = ''
        data['target_comment'] = ''

    # Actual
    actual_elem = period_elem.find('actual')
    if actual_elem is not None:
        data['actual_value'] = actual_elem.get('value', '')
        actual_comment = actual_elem.find('comment/narrative')
        data['actual_comment'] = get_text_content(actual_comment)
    else:
        data['actual_value'] = ''
        data['actual_comment'] = ''

    return data


def extract_transaction_sector_data(
    sector_elem: ET.Element,
    activity_id: str,
    transaction_ref: str,
    transaction_type: str
) -> Dict[str, str]:
    """Extract transaction sector data."""
    data = {
        'activity_identifier': activity_id,
        'transaction_ref': transaction_ref,
        'transaction_type': transaction_type
    }

    data['sector_code'] = sector_elem.get('code', '')
    data['vocabulary'] = sector_elem.get('vocabulary', '1')
    data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')

    sector_name = sector_elem.find('narrative')
    data['sector_name'] = get_text_content(sector_name)

    return data


def extract_country_budget_items(
    cbi_elem: ET.Element,
    activity_id: str
) -> List[Dict[str, str]]:
    """Extract country budget items."""
    items = []
    vocabulary = cbi_elem.get('vocabulary', '')

    for item_elem in cbi_elem.findall('budget-item'):
        data = {
            'activity_identifier': activity_id,
            'vocabulary': vocabulary,
            'budget_item_code': item_elem.get('code', ''),
            'budget_item_percentage': item_elem.get('percentage', '')
        }

        # Description
        desc_elem = item_elem.find('description/narrative')
        if desc_elem is not None:
            data['description'] = get_text_content(desc_elem)
            data['description_lang'] = desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        else:
            data['description'] = ''
            data['description_lang'] = ''

        items.append(data)

    return items


def extract_main_activity_data(activity_elem: ET.Element, activity_id: str, csv_files_config: Dict) -> Dict[str, str]:
    """Extract main activity information."""
    data = {'activity_identifier': activity_id}
    xml_lang_attr = '{http://www.w3.org/XML/1998/namespace}lang'

    # Basic attributes
    data['default_currency'] = activity_elem.get('default-currency', '')
    # Preserve exact humanitarian value: "" (missing), "0" (explicit false), "1" (explicit true)
    data['humanitarian'] = activity_elem.get('humanitarian', '')
    data['hierarchy'] = activity_elem.get('hierarchy', '')
    data['last_updated_datetime'] = activity_elem.get('last-updated-datetime', '')
    data['xml_lang'] = activity_elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')

    # Title - extract lang attribute from narrative
    title_elem = activity_elem.find('title/narrative')
    data['title'] = get_text_content(title_elem)
    data['title_lang'] = title_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if title_elem is not None else ''

    # Description - extract lang attribute from narrative
    desc_elem = activity_elem.find('description[@type="1"]/narrative')
    if desc_elem is None:
        desc_elem = activity_elem.find('description/narrative')
    data['description'] = get_text_content(desc_elem)
    data['description_lang'] = (
        desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if desc_elem is not None else ''
    )

    # Activity status
    status_elem = activity_elem.find('activity-status')
    data['activity_status'] = status_elem.get('code') if status_elem is not None else ''

    # Activity scope
    scope_elem = activity_elem.find('activity-scope')
    data['activity_scope'] = scope_elem.get('code') if scope_elem is not None else ''

    # Reporting organization - extract lang from narrative
    rep_org_elem = activity_elem.find('reporting-org')
    if rep_org_elem is not None:
        data['reporting_org_ref'] = rep_org_elem.get('ref', '')
        data['reporting_org_type'] = rep_org_elem.get('type', '')
        rep_org_name = rep_org_elem.find('narrative')
        data['reporting_org_name'] = get_text_content(rep_org_name)
        data['reporting_org_name_lang'] = (
            rep_org_name.get('{http://www.w3.org/XML/1998/namespace}lang', '') if rep_org_name is not None else ''
        )
        data['reporting_org_secondary_reporter'] = rep_org_elem.get('secondary-reporter', '')
        data['reporting_org_role'] = rep_org_elem.get('role', '')
    else:
        data['reporting_org_ref'] = ''
        data['reporting_org_type'] = ''
        data['reporting_org_name'] = ''
        data['reporting_org_name_lang'] = ''
        data['reporting_org_secondary_reporter'] = ''
        data['reporting_org_role'] = ''

    # Recipient country (first one only for main table)
    country_elem = activity_elem.find('recipient-country')
    if country_elem is not None:
        data['recipient_country_code'] = country_elem.get('code', '')
        country_name = country_elem.find('narrative')
        data['recipient_country_name'] = get_text_content(country_name)
        data['recipient_country_lang'] = (
            country_name.get(xml_lang_attr, '') if country_name is not None else ''
        )
        data['recipient_country_percentage'] = country_elem.get('percentage', '')
    else:
        data['recipient_country_code'] = ''
        data['recipient_country_name'] = ''
        data['recipient_country_lang'] = ''
        data['recipient_country_percentage'] = ''

    # Recipient region (first one only for main table)
    region_elem = activity_elem.find('recipient-region')
    if region_elem is not None:
        data['recipient_region_code'] = region_elem.get('code', '')
        region_name = region_elem.find('narrative')
        data['recipient_region_name'] = get_text_content(region_name)
        data['recipient_region_lang'] = (
            region_name.get(xml_lang_attr, '') if region_name is not None else ''
        )
        data['recipient_region_percentage'] = region_elem.get('percentage', '')
    else:
        data['recipient_region_code'] = ''
        data['recipient_region_name'] = ''
        data['recipient_region_lang'] = ''
        data['recipient_region_percentage'] = ''

    # Default flow/finance/aid/tied status and collaboration type
    collab_elem = activity_elem.find('collaboration-type')
    data['collaboration_type'] = collab_elem.get('code') if collab_elem is not None else ''

    flow_elem = activity_elem.find('default-flow-type')
    data['default_flow_type'] = flow_elem.get('code') if flow_elem is not None else ''

    finance_elem = activity_elem.find('default-finance-type')
    data['default_finance_type'] = finance_elem.get('code') if finance_elem is not None else ''

    aid_elem = activity_elem.find('default-aid-type')
    data['default_aid_type'] = aid_elem.get('code') if aid_elem is not None else ''
    data['default_aid_type_vocabulary'] = aid_elem.get('vocabulary') if aid_elem is not None else ''

    tied_elem = activity_elem.find('default-tied-status')
    data['default_tied_status'] = tied_elem.get('code') if tied_elem is not None else ''

    # Conditions attached
    conditions_elem = activity_elem.find('conditions')
    data['conditions_attached'] = conditions_elem.get('attached', '') if conditions_elem is not None else ''

    # Fill in empty values for missing columns
    for col in csv_files_config['activities']['columns']:
        if col not in data:
            data[col] = ''

    return data


def extract_condition_data(condition_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract individual condition data."""
    data = {
        'activity_identifier': activity_id,
        'condition_type': condition_elem.get('type', ''),
        'condition_text': get_text_content(condition_elem.find('narrative'))
    }
    return data


def extract_participating_org_data(org_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract participating organization data."""
    data = {'activity_identifier': activity_id}

    data['org_ref'] = org_elem.get('ref', '')
    data['org_type'] = org_elem.get('type', '')
    data['role'] = org_elem.get('role', '')
    data['activity_id'] = org_elem.get('activity-id', '')
    data['crs_channel_code'] = org_elem.get('crs-channel-code', '')

    org_name = org_elem.find('narrative')
    data['org_name'] = get_text_content(org_name)
    data['org_name_lang'] = (
        org_name.get('{http://www.w3.org/XML/1998/namespace}lang', '') if org_name is not None else ''
    )

    return data


def extract_sector_data(sector_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract sector data."""
    data = {'activity_identifier': activity_id}

    data['sector_code'] = sector_elem.get('code', '')
    data['vocabulary'] = sector_elem.get('vocabulary', '1')
    data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')
    data['percentage'] = sector_elem.get('percentage', '')

    sector_name = sector_elem.find('narrative')
    data['sector_name'] = get_text_content(sector_name)

    return data


def extract_budget_data(budget_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract budget data."""
    data = {'activity_identifier': activity_id}

    data['budget_type'] = budget_elem.get('type', '')
    data['budget_status'] = budget_elem.get('status', '')

    period_start = budget_elem.find('period-start')
    data['period_start'] = period_start.get('iso-date') if period_start is not None else ''

    period_end = budget_elem.find('period-end')
    data['period_end'] = period_end.get('iso-date') if period_end is not None else ''

    value_elem = budget_elem.find('value')
    if value_elem is not None:
        data['value'] = get_text_content(value_elem)
        data['currency'] = value_elem.get('currency', '')
        data['value_date'] = value_elem.get('value-date', '')
    else:
        data['value'] = ''
        data['currency'] = ''
        data['value_date'] = ''

    return data


def extract_transaction_data(trans_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract transaction data."""
    xml_lang = '{http://www.w3.org/XML/1998/namespace}lang'
    data = {'activity_identifier': activity_id}

    data['transaction_ref'] = trans_elem.get('ref', '')
    # Preserve exact humanitarian value: "" (missing), "0" (explicit false), "1" (explicit true)
    data['humanitarian'] = trans_elem.get('humanitarian', '')

    # Transaction type
    type_elem = trans_elem.find('transaction-type')
    data['transaction_type'] = type_elem.get('code') if type_elem is not None else ''

    # Transaction date
    date_elem = trans_elem.find('transaction-date')
    data['transaction_date'] = date_elem.get('iso-date') if date_elem is not None else ''

    # Value
    value_elem = trans_elem.find('value')
    if value_elem is not None:
        data['value'] = get_text_content(value_elem)
        data['currency'] = value_elem.get('currency', '')
        data['value_date'] = value_elem.get('value-date', '')
    else:
        data['value'] = ''
        data['currency'] = ''
        data['value_date'] = ''

    # Description
    desc_elem = trans_elem.find('description/narrative')
    data['description'] = get_text_content(desc_elem)
    data['description_lang'] = (
        desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if desc_elem is not None else ''
    )

    # Provider org
    provider_elem = trans_elem.find('provider-org')
    if provider_elem is not None:
        data['provider_org_ref'] = provider_elem.get('ref', '')
        data['provider_org_type'] = provider_elem.get('type', '')
        provider_name = provider_elem.find('narrative')
        data['provider_org_name'] = get_text_content(provider_name)
        data['provider_org_lang'] = provider_name.get(xml_lang, '') if provider_name is not None else ''
    else:
        data['provider_org_ref'] = ''
        data['provider_org_type'] = ''
        data['provider_org_name'] = ''
        data['provider_org_lang'] = ''

    # Receiver org
    receiver_elem = trans_elem.find('receiver-org')
    if receiver_elem is not None:
        data['receiver_org_ref'] = receiver_elem.get('ref', '')
        data['receiver_org_type'] = receiver_elem.get('type', '')
        data['receiver_org_activity_id'] = receiver_elem.get('receiver-activity-id', '')
        receiver_name = receiver_elem.find('narrative')
        data['receiver_org_name'] = get_text_content(receiver_name)
        data['receiver_org_lang'] = receiver_name.get(xml_lang, '') if receiver_name is not None else ''
    else:
        data['receiver_org_ref'] = ''
        data['receiver_org_type'] = ''
        data['receiver_org_name'] = ''
        data['receiver_org_activity_id'] = ''
        data['receiver_org_lang'] = ''

    # Additional fields
    data['disbursement_channel'] = ''
    data['flow_type'] = ''
    data['finance_type'] = ''
    data['aid_type'] = ''
    data['aid_type_vocabulary'] = ''
    data['tied_status'] = ''
    data['recipient_region'] = ''

    # Extract additional transaction elements
    disbursement_elem = trans_elem.find('disbursement-channel')
    if disbursement_elem is not None:
        data['disbursement_channel'] = disbursement_elem.get('code', '')

    flow_type_elem = trans_elem.find('flow-type')
    if flow_type_elem is not None:
        data['flow_type'] = flow_type_elem.get('code', '')

    finance_type_elem = trans_elem.find('finance-type')
    if finance_type_elem is not None:
        data['finance_type'] = finance_type_elem.get('code') if finance_type_elem.get('code') != '0' else ''

    aid_type_elem = trans_elem.find('aid-type')
    if aid_type_elem is not None:
        data['aid_type'] = aid_type_elem.get('code') if aid_type_elem.get('code') != '0' else ''
        data['aid_type_vocabulary'] = aid_type_elem.get('vocabulary', '')

    tied_status_elem = trans_elem.find('tied-status')
    if tied_status_elem is not None:
        data['tied_status'] = tied_status_elem.get('code') if tied_status_elem.get('code') != '0' else ''

    recipient_region_elem = trans_elem.find('recipient-region')
    if recipient_region_elem is not None:
        data['recipient_region'] = recipient_region_elem.get('code', '')

    return data


def extract_location_data(location_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract location data."""
    data = {'activity_identifier': activity_id}
    xml_lang = '{http://www.w3.org/XML/1998/namespace}lang'

    data['location_ref'] = location_elem.get('ref', '')
    data['location_reach'] = location_elem.get('reach', '')

    # Location ID
    loc_id_elem = location_elem.find('location-id')
    if loc_id_elem is not None:
        data['location_id_vocabulary'] = loc_id_elem.get('vocabulary', '')
        data['location_id_code'] = loc_id_elem.get('code', '')
    else:
        data['location_id_vocabulary'] = ''
        data['location_id_code'] = ''

    # Names and descriptions
    name_elem = location_elem.find('name/narrative')
    data['name'] = get_text_content(name_elem)
    data['name_lang'] = name_elem.get(xml_lang, '') if name_elem is not None else ''

    desc_elem = location_elem.find('description/narrative')
    data['description'] = get_text_content(desc_elem)
    data['description_lang'] = desc_elem.get(xml_lang, '') if desc_elem is not None else ''

    activity_desc_elem = location_elem.find('activity-description/narrative')
    data['activity_description'] = get_text_content(activity_desc_elem)
    data['activity_description_lang'] = activity_desc_elem.get(xml_lang, '') if activity_desc_elem is not None else ''

    # Coordinates
    point_elem = location_elem.find('point/pos')
    if point_elem is not None and point_elem.text:
        coords = get_text_content(point_elem).split()
        if len(coords) >= 2:
            data['latitude'] = coords[0]
            data['longitude'] = coords[1]
        else:
            data['latitude'] = ''
            data['longitude'] = ''
    else:
        data['latitude'] = ''
        data['longitude'] = ''

    # Additional location attributes
    data['exactness'] = location_elem.get('exactness', '')
    data['location_class'] = location_elem.get('class', '')
    data['feature_designation'] = location_elem.get('feature-designation', '')

    # Administrative
    admin_elem = location_elem.find('administrative')
    if admin_elem is not None:
        data['administrative_vocabulary'] = admin_elem.get('vocabulary', '')
        data['administrative_level'] = admin_elem.get('level', '')
        data['administrative_code'] = admin_elem.get('code', '')
        data['administrative_country'] = admin_elem.get('country', '')
    else:
        data['administrative_vocabulary'] = ''
        data['administrative_level'] = ''
        data['administrative_code'] = ''
        data['administrative_country'] = ''

    return data


def extract_document_data(doc_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract document data."""
    data = {'activity_identifier': activity_id}

    data['url'] = doc_elem.get('url', '')
    data['format'] = doc_elem.get('format', '')
    data['document_date'] = doc_elem.get('document-date', '')

    title_elem = doc_elem.find('title/narrative')
    data['title'] = get_text_content(title_elem)
    data['title_lang'] = (
        title_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if title_elem is not None else ''
    )

    desc_elem = doc_elem.find('description/narrative')
    data['description'] = get_text_content(desc_elem)
    data['description_lang'] = (
        desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if desc_elem is not None else ''
    )

    category_elem = doc_elem.find('category')
    data['category_code'] = category_elem.get('code') if category_elem is not None else ''

    lang_elem = doc_elem.find('language')
    data['language_code'] = lang_elem.get('code') if lang_elem is not None else ''

    return data


def extract_result_data(
    result_elem: ET.Element,
    activity_id: str,
    result_index: int = 1
) -> Dict[str, str]:
    """Extract result data."""
    data = {'activity_identifier': activity_id}

    data['result_ref'] = result_elem.get('ref', f"result_{result_index}")
    data['result_type'] = result_elem.get('type', '')
    data['aggregation_status'] = result_elem.get('aggregation-status', '')

    title_elem = result_elem.find('title/narrative')
    data['title'] = get_text_content(title_elem)

    desc_elem = result_elem.find('description/narrative')
    data['description'] = get_text_content(desc_elem)

    return data


def extract_indicator_data(
    indicator_elem: ET.Element,
    activity_id: str,
    result_ref: str,
    indicator_index: int = 1
) -> Dict[str, str]:
    """Extract indicator data."""
    indicator_ref = f'indicator_{activity_id}_{result_ref}_{indicator_index}'

    data = {
        'activity_identifier': activity_id,
        'result_ref': result_ref,
        'indicator_ref': indicator_ref
    }

    # Measure
    measure = indicator_elem.get('measure')
    if measure:
        data['indicator_measure'] = measure

    # Ascending
    ascending = indicator_elem.get('ascending')
    if ascending:
        data['ascending'] = ascending

    # Aggregation status
    aggregation_status = indicator_elem.get('aggregation-status')
    if aggregation_status:
        data['aggregation_status'] = aggregation_status

    # Title
    title_elem = indicator_elem.find('title')
    if title_elem is not None:
        narrative = title_elem.find('narrative')
        if narrative is not None:
            data['title'] = get_text_content(narrative).strip()

    # Description
    desc_elem = indicator_elem.find('description')
    if desc_elem is not None:
        narrative = desc_elem.find('narrative')
        if narrative is not None:
            data['description'] = get_text_content(narrative).strip()

    # Baseline
    baseline_elem = indicator_elem.find('baseline')
    if baseline_elem is not None:
        data['baseline_year'] = baseline_elem.get('year', '')
        data['baseline_iso_date'] = baseline_elem.get('iso-date', '')
        data['baseline_value'] = baseline_elem.get('value', '')

        comment = baseline_elem.find('comment/narrative')
        if comment is not None:
            data['baseline_comment'] = get_text_content(comment).strip()

    return data


def extract_contact_data(contact_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract contact information data."""
    data = {'activity_identifier': activity_id}

    data['contact_type'] = contact_elem.get('type', '')

    org_elem = contact_elem.find('organisation/narrative')
    data['organisation'] = get_text_content(org_elem)
    data['organisation_lang'] = (
        org_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if org_elem is not None else ''
    )

    dept_elem = contact_elem.find('department/narrative')
    data['department'] = get_text_content(dept_elem)
    data['department_lang'] = (
        dept_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if dept_elem is not None else ''
    )

    person_elem = contact_elem.find('person-name/narrative')
    data['person_name'] = get_text_content(person_elem)
    data['person_name_lang'] = (
        person_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if person_elem is not None else ''
    )
    data['person_name_present'] = '1' if person_elem is not None else '0'

    job_elem = contact_elem.find('job-title/narrative')
    data['job_title'] = get_text_content(job_elem)
    data['job_title_lang'] = (
        job_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if job_elem is not None else ''
    )

    tel_elem = contact_elem.find('telephone')
    data['telephone'] = get_text_content(tel_elem)

    email_elem = contact_elem.find('email')
    data['email'] = get_text_content(email_elem)
    data['email_present'] = '1' if email_elem is not None else '0'

    website_elem = contact_elem.find('website')
    data['website'] = get_text_content(website_elem)

    addr_elem = contact_elem.find('mailing-address/narrative')
    data['mailing_address'] = get_text_content(addr_elem)
    data['mailing_address_lang'] = (
        addr_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if addr_elem is not None else ''
    )

    return data


def extract_activity_date_data(date_elem: ET.Element, activity_id: str) -> Dict[str, str]:
    """Extract activity date data."""
    data = {'activity_identifier': activity_id}

    data['type'] = date_elem.get('type')
    iso_date = date_elem.get('iso-date', '')
    data['iso_date'] = iso_date

    # Get narrative if exists (it's optional)
    narrative = date_elem.find('narrative')
    if narrative is not None:
        data['narrative'] = get_text_content(narrative)
        data['narrative_lang'] = narrative.get('{http://www.w3.org/XML/1998/namespace}lang', '')
    else:
        data['narrative'] = ''
        data['narrative_lang'] = ''

    return data
