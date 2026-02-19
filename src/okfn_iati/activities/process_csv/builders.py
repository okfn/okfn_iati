"""
IATI CSV to XML builders module.

This module contains all functions for building IATI model objects from CSV row data.
"""

from typing import List, Dict, Any, Optional

from ...models import (
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    Location, DocumentLink, Budget, Transaction, Result,
    ContactInfo, Indicator, IndicatorBaseline, IndicatorPeriod,
    IndicatorPeriodTarget, IndicatorPeriodActual
)
from ...enums import ActivityStatus, ActivityDateType, DocumentCategory, ActivityScope, CollaborationType


def safe_int(value: Optional[str], default: int = 0) -> int:
    """Safely convert string values to integers for ordering."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def parse_activity_status(status_code: str) -> Optional[ActivityStatus]:
    """Parse activity status code to enum."""
    if not status_code:
        return None
    try:
        return ActivityStatus(int(status_code))
    except (ValueError, TypeError):
        return None


def parse_activity_scope(scope_code: str) -> Optional[ActivityScope]:
    """Parse activity scope code to enum."""
    if not scope_code:
        return None
    try:
        return ActivityScope(scope_code)
    except (ValueError, TypeError):
        return None


def build_activity_date(date_data: Dict[str, str]) -> ActivityDate:
    """Build ActivityDate from data."""
    narratives = []
    if date_data.get('narrative'):
        narratives.append(Narrative(
            text=date_data['narrative'],
            lang=date_data.get('narrative_lang', '')
        ))

    return ActivityDate(
        type=ActivityDateType(date_data['type']),
        iso_date=date_data.get('iso_date', ''),
        narratives=narratives
    )


def add_dates_from_main_data(activity: Activity, main_data: Dict[str, str]) -> None:
    """Add activity dates from main data."""
    date_mappings = [
        ('planned_start_date', ActivityDateType.PLANNED_START),
        ('actual_start_date', ActivityDateType.ACTUAL_START),
        ('planned_end_date', ActivityDateType.PLANNED_END),
        ('actual_end_date', ActivityDateType.ACTUAL_END)
    ]

    for date_field, date_type in date_mappings:
        date_value = main_data.get(date_field)
        if date_value:
            try:
                activity_date = ActivityDate(
                    type=date_type,
                    iso_date=date_value
                )
                activity.activity_dates.append(activity_date)
            except ValueError:
                # Skip invalid dates
                continue


def add_geography_from_main_data(activity: Activity, main_data: Dict[str, str]) -> None:
    """Add recipient countries and regions from main data."""
    # Add recipient country if present
    country_code = main_data.get('recipient_country_code')
    percentage = main_data.get('recipient_country_percentage')
    if country_code:
        country_data = {'code': country_code}
        if percentage:
            country_data['percentage'] = percentage
        country_name = main_data.get('recipient_country_name')
        country_lang = main_data.get('recipient_country_lang') or None
        if country_name or country_lang:
            country_data['narratives'] = [Narrative(
                text=country_name or '',
                lang=country_lang
            )]
        activity.recipient_countries.append(country_data)

    # Add recipient region if present
    region_code = main_data.get('recipient_region_code')
    percentage = main_data.get('recipient_region_percentage')
    if region_code:
        region_data = {'code': region_code}
        if percentage:
            region_data['percentage'] = percentage
        region_name = main_data.get('recipient_region_name')
        region_lang = main_data.get('recipient_region_lang') or None
        if region_name or region_lang:
            region_data['narratives'] = [Narrative(
                text=region_name or '',
                lang=region_lang
            )]
        activity.recipient_regions.append(region_data)


def add_default_types_from_main_data(activity: Activity, main_data: Dict[str, str]) -> None:
    """Add collaboration type from main data."""
    # Add collaboration type if present
    collaboration_type = main_data.get('collaboration_type')
    if collaboration_type:
        try:
            activity.collaboration_type = CollaborationType(collaboration_type)
        except (ValueError, TypeError):
            pass  # Skip invalid collaboration type


def build_participating_org(org_data: Dict[str, str]) -> ParticipatingOrg:
    """Build ParticipatingOrg from data."""
    narratives = []
    if org_data.get('org_name') or org_data.get('org_name_lang'):
        narratives.append(Narrative(
            text=org_data.get('org_name', ''),
            lang=org_data.get('org_name_lang') or None
        ))

    return ParticipatingOrg(
        role=org_data.get('role', '1'),
        ref=org_data.get('org_ref', ''),
        type=org_data.get('org_type', ''),
        activity_id=org_data.get('activity_id'),
        crs_channel_code=org_data.get('crs_channel_code'),
        narratives=narratives
    )


def build_sector(sector_data: Dict[str, str]) -> Dict[str, Any]:
    """Build sector from data."""
    sector = {
        "code": sector_data.get('sector_code', ''),
        "vocabulary": sector_data.get('vocabulary', '1')
    }

    if sector_data.get('vocabulary_uri'):
        sector["vocabulary_uri"] = sector_data['vocabulary_uri']

    if sector_data.get('percentage'):
        sector["percentage"] = sector_data['percentage']

    if sector_data.get('sector_name'):
        sector["narratives"] = [Narrative(text=sector_data['sector_name'])]

    return sector


def build_budget(budget_data: Dict[str, str]) -> Budget:
    """Build Budget from data."""
    value_text = budget_data.get('value', '') or ''
    try:
        numeric_value = float(value_text) if value_text else 0.0
    except ValueError:
        numeric_value = 0.0

    return Budget(
        type=budget_data.get('budget_type', '1'),
        status=budget_data.get('budget_status', '1'),
        period_start=budget_data.get('period_start', ''),
        period_end=budget_data.get('period_end', ''),
        value=numeric_value,
        currency=budget_data.get('currency', 'USD'),
        value_date=budget_data.get('value_date', ''),
        raw_value=value_text
    )


def build_transaction( # noqa C901
    trans_data: Dict[str, str],
    trans_sectors: Optional[List[Dict[str, str]]] = None
) -> Transaction:
    """Build Transaction from data."""
    # Parse humanitarian: "" -> None, "0" -> False, "1" -> True
    humanitarian_value = trans_data.get('humanitarian', '')
    if humanitarian_value == '':
        humanitarian = None
    elif humanitarian_value == '0':
        humanitarian = False
    else:  # '1' or any other truthy value
        humanitarian = True

    value_text = trans_data.get('value', '') or ''
    try:
        value_numeric = float(value_text) if value_text else 0.0
    except ValueError:
        value_numeric = 0.0

    transaction_args = {
        'type': trans_data.get('transaction_type', '2'),
        'date': trans_data.get('transaction_date', ''),
        'value': value_numeric,
        'currency': trans_data.get('currency', 'USD'),
        'value_date': trans_data.get('value_date', ''),
        'transaction_ref': trans_data.get('transaction_ref'),
        'humanitarian': humanitarian,
        'raw_value': value_text,
    }

    if trans_data.get('description') or trans_data.get('description_lang'):
        transaction_args['description'] = [Narrative(
            text=trans_data.get('description', ''),
            lang=trans_data.get('description_lang') or None
        )]

    # Add provider org
    if trans_data.get('provider_org_ref') or trans_data.get('provider_org_name') or trans_data.get('provider_org_lang'):
        transaction_args['provider_org'] = OrganizationRef(
            ref=trans_data.get('provider_org_ref', ''),
            type=trans_data.get('provider_org_type', ''),
            narratives=[
                Narrative(
                    text=trans_data.get('provider_org_name', ''),
                    lang=trans_data.get('provider_org_lang') or None
                )
            ] if (trans_data.get('provider_org_name') or trans_data.get('provider_org_lang')) else [],
            receiver_org_activity_id=trans_data.get('receiver_org_activity_id', ''),
        )

    # Add receiver org
    if trans_data.get('receiver_org_ref') or trans_data.get('receiver_org_name') or trans_data.get('receiver_org_lang'):
        transaction_args['receiver_org'] = OrganizationRef(
            ref=trans_data.get('receiver_org_ref', ''),
            type=trans_data.get('receiver_org_type', ''),
            narratives=[
                Narrative(
                    text=trans_data.get('receiver_org_name', ''),
                    lang=trans_data.get('receiver_org_lang') or None
                )
            ] if (trans_data.get('receiver_org_name') or trans_data.get('receiver_org_lang')) else [],
            receiver_org_activity_id=trans_data.get('receiver_org_activity_id', ''),
        )

    # Add optional fields
    if trans_data.get('disbursement_channel'):
        transaction_args['disbursement_channel'] = trans_data['disbursement_channel']
    if trans_data.get('flow_type'):
        transaction_args['flow_type'] = trans_data['flow_type']
    if trans_data.get('finance_type'):
        transaction_args['finance_type'] = trans_data['finance_type']
    if trans_data.get('tied_status'):
        transaction_args['tied_status'] = trans_data['tied_status']
    if trans_data.get('aid_type'):
        vocab = trans_data.get('aid_type_vocabulary') or "1"
        transaction_args['aid_type'] = {"code": trans_data['aid_type'], "vocabulary": vocab}
        transaction_args['aid_type_vocabulary'] = vocab
    if trans_data.get('recipient_region'):
        transaction_args['recipient_region'] = trans_data['recipient_region']

    sectors = []
    if trans_sectors:
        for sector_data in trans_sectors:
            sector = {
                "code": sector_data.get('sector_code', ''),
                "vocabulary": sector_data.get('vocabulary', '1'),
            }
            if sector_data.get('vocabulary_uri'):
                sector['vocabulary_uri'] = sector_data['vocabulary_uri']
            if sector_data.get('sector_name'):
                sector['narratives'] = [Narrative(text=sector_data['sector_name'])]
            sectors.append(sector)
    transaction_args['sectors'] = sectors

    return Transaction(**transaction_args)


def build_location(location_data: Dict[str, str]) -> Location:
    """Build Location from data."""
    location_args: Dict[str, Any] = {}

    if location_data.get('location_ref'):
        location_args['ref'] = location_data['location_ref']

    if location_data.get('name') or location_data.get('name_lang'):
        location_args['name'] = [Narrative(
            text=location_data.get('name', ''),
            lang=location_data.get('name_lang') or None
        )]

    if location_data.get('description') or location_data.get('description_lang'):
        location_args['description'] = [Narrative(
            text=location_data.get('description', ''),
            lang=location_data.get('description_lang') or None
        )]

    if location_data.get('activity_description') or location_data.get('activity_description_lang'):
        location_args['activity_description'] = [Narrative(
            text=location_data.get('activity_description', ''),
            lang=location_data.get('activity_description_lang') or None
        )]

    if location_data.get('latitude') and location_data.get('longitude'):
        location_args['point'] = {
            'srsName': 'http://www.opengis.net/def/crs/EPSG/0/4326',
            'pos': f"{location_data['latitude']} {location_data['longitude']}"
        }

    return Location(**location_args)


def build_document(doc_data: Dict[str, str]) -> DocumentLink:
    """Build DocumentLink from data."""
    doc_args = {
        'url': doc_data.get('url', ''),
        'format': doc_data.get('format', 'application/pdf')
    }

    if doc_data.get('title') or doc_data.get('title_lang'):
        doc_args['title'] = [Narrative(
            text=doc_data.get('title', ''),
            lang=doc_data.get('title_lang') or None
        )]

    if doc_data.get('category_code'):
        doc_args['categories'] = [DocumentCategory(doc_data['category_code'])]

    if doc_data.get('description') or doc_data.get('description_lang'):
        doc_args['description'] = [Narrative(
            text=doc_data.get('description', ''),
            lang=doc_data.get('description_lang') or None
        )]

    return DocumentLink(**doc_args)


def build_contact_info(contact_data: Dict[str, str]) -> ContactInfo:
    """Build ContactInfo from data."""
    contact_args = {}

    if contact_data.get('contact_type'):
        contact_args['type'] = contact_data['contact_type']

    if contact_data.get('organisation') or contact_data.get('organisation_lang'):
        contact_args['organisation'] = [Narrative(
            text=contact_data.get('organisation', ''),
            lang=contact_data.get('organisation_lang') or None
        )]

    if contact_data.get('department') or contact_data.get('department_lang'):
        contact_args['department'] = [Narrative(
            text=contact_data.get('department', ''),
            lang=contact_data.get('department_lang') or None
        )]

    person_present = contact_data.get('person_name_present') == '1'
    if person_present or contact_data.get('person_name') or contact_data.get('person_name_lang'):
        contact_args['person_name'] = [Narrative(
            text=contact_data.get('person_name', ''),
            lang=contact_data.get('person_name_lang') or None
        )]

    if contact_data.get('job_title') or contact_data.get('job_title_lang'):
        contact_args['job_title'] = [Narrative(
            text=contact_data.get('job_title', ''),
            lang=contact_data.get('job_title_lang') or None
        )]

    if contact_data.get('telephone'):
        contact_args['telephone'] = contact_data['telephone']

    email_present = contact_data.get('email_present') == '1'
    if email_present or contact_data.get('email'):
        contact_args['email'] = contact_data.get('email', '')

    if contact_data.get('website'):
        contact_args['website'] = contact_data['website']

    if contact_data.get('mailing_address') or contact_data.get('mailing_address_lang'):
        contact_args['mailing_address'] = [Narrative(
            text=contact_data.get('mailing_address', ''),
            lang=contact_data.get('mailing_address_lang') or None
        )]

    return ContactInfo(**contact_args)


def build_result_with_indicators(
    result_data: Dict[str, str],
    indicators_data: List[Dict[str, str]],
    periods_data: List[Dict[str, str]]
) -> Result:
    """Build Result with its indicators and periods."""
    result_args = {
        'type': result_data.get('result_type', '1')
    }

    if result_data.get('title'):
        result_args['title'] = [Narrative(text=result_data['title'])]

    if result_data.get('description'):
        result_args['description'] = [Narrative(text=result_data['description'])]

    if result_data.get('aggregation_status'):
        result_args['aggregation_status'] = result_data['aggregation_status'].lower() in ('true', '1', 'yes')

    # BUILD INDICATORS FOR THIS RESULT
    indicators = []
    for indicator_data in indicators_data:
        indicator = build_indicator(indicator_data)

        # Add periods to this indicator
        indicator_ref = indicator_data.get('indicator_ref', '')
        for period_data in periods_data:
            if period_data.get('indicator_ref') == indicator_ref:
                period = build_indicator_period(period_data)
                if indicator.period is None:
                    indicator.period = []
                indicator.period.append(period)

        indicators.append(indicator)

    result_args['indicator'] = indicators
    return Result(**result_args)


def build_indicator(indicator_data: Dict[str, str]) -> Indicator:
    """Build Indicator from data."""
    indicator_args = {
        'measure': indicator_data.get('indicator_measure', '1')
    }

    if indicator_data.get('title'):
        indicator_args['title'] = [Narrative(text=indicator_data['title'])]

    if indicator_data.get('description'):
        indicator_args['description'] = [Narrative(text=indicator_data['description'])]

    if indicator_data.get('ascending'):
        indicator_args['ascending'] = indicator_data['ascending'].lower() in ('true', '1', 'yes')

    if indicator_data.get('aggregation_status'):
        indicator_args['aggregation_status'] = indicator_data['aggregation_status'].lower() in ('true', '1', 'yes')

    # Add baseline if present
    if indicator_data.get('baseline_year'):
        try:
            baseline = IndicatorBaseline(
                year=int(indicator_data['baseline_year']),
                iso_date=indicator_data.get('baseline_iso_date'),
                value=indicator_data.get('baseline_value')
            )
            if indicator_data.get('baseline_comment'):
                baseline.comment = [Narrative(text=indicator_data['baseline_comment'])]
            indicator_args['baseline'] = [baseline]
        except (ValueError, TypeError):
            pass  # Skip invalid baseline data

    return Indicator(**indicator_args)


def build_indicator_period(period_data: Dict[str, str]) -> IndicatorPeriod:
    """Build IndicatorPeriod from data."""
    period_args = {
        'period_start': period_data.get('period_start', ''),
        'period_end': period_data.get('period_end', '')
    }

    # Add target if present
    if period_data.get('target_value'):
        target = IndicatorPeriodTarget(value=period_data['target_value'])
        if period_data.get('target_comment'):
            target.comment = [Narrative(text=period_data['target_comment'])]
        period_args['target'] = [target]

    # Add actual if present
    if period_data.get('actual_value'):
        actual = IndicatorPeriodActual(value=period_data['actual_value'])
        if period_data.get('actual_comment'):
            actual.comment = [Narrative(text=period_data['actual_comment'])]
        period_args['actual'] = [actual]

    return IndicatorPeriod(**period_args)


def build_country_budget_items(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Build country budget items from CSV rows."""
    if not rows:
        return []

    # Group by vocabulary
    grouped_items = {}
    for row in rows:
        vocab = row.get('vocabulary', '')
        if vocab not in grouped_items:
            grouped_items[vocab] = []
        grouped_items[vocab].append(row)

    result = []
    for vocab, items in grouped_items.items():
        cbi_data = {
            'vocabulary': vocab,
            'budget_items': []
        }

        for item in items:
            budget_item = {
                'code': item.get('budget_item_code', ''),
                'percentage': item.get('budget_item_percentage', '')
            }

            if item.get('description'):
                budget_item['description'] = [{
                    'text': item['description'],
                    'lang': item.get('description_lang', '')
                }]

            cbi_data['budget_items'].append(budget_item)

        result.append(cbi_data)

    return result


def build_descriptions_from_rows(
    rows: List[Dict[str, str]]
) -> List[Dict[str, List[Narrative]]]:
    """Reconstruct description structures from CSV rows."""
    if not rows:
        return []

    grouped: Dict[str, Dict[str, Any]] = {}
    for row in sorted(
        rows,
        key=lambda r: (
            safe_int(r.get('description_sequence')),
            safe_int(r.get('narrative_sequence'))
        )
    ):
        seq = row.get('description_sequence') or str(len(grouped) + 1)
        entry = grouped.setdefault(seq, {
            'type': row.get('description_type', ''),
            'narratives': []
        })
        text = row.get('narrative', '') or ''
        lang = row.get('narrative_lang') or None
        entry['narratives'].append(Narrative(text=text, lang=lang))

    descriptions: List[Dict[str, List[Narrative]]] = []
    for seq in sorted(grouped.keys(), key=safe_int):
        entry = grouped[seq]
        desc_dict: Dict[str, Any] = {
            "narratives": entry['narratives'] or [Narrative(text='')]
        }
        if entry['type']:
            desc_dict["type"] = entry['type']
        descriptions.append(desc_dict)

    return descriptions
