"""
IATI CSV Converter - Bidirectional conversion between IATI XML and CSV formats.

This module provides utilities to convert IATI XML data to/from CSV format,
making it easier for users to work with IATI data using familiar tools like Excel.
"""

import csv
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Union
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from .models import (
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    Location, DocumentLink, Budget, Transaction, Result, IatiActivities, ContactInfo
)
from .enums import (
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, ContactType, DocumentCategory
)
from .xml_generator import IatiXmlGenerator


class IatiCsvConverter:
    """
    Bidirectional converter between IATI XML and CSV formats.

    This class provides methods to:
    1. Convert IATI XML files to CSV format
    2. Convert CSV files to IATI XML format
    3. Generate CSV templates for data entry
    """

    # Define the standard CSV column structure
    CSV_COLUMNS = [
        # Basic Activity Information
        'activity_identifier',
        'title',
        'description',
        'activity_status',
        'default_currency',
        'humanitarian',

        # Organization Information
        'reporting_org_ref',
        'reporting_org_name',
        'reporting_org_type',

        # Dates
        'planned_start_date',
        'actual_start_date',
        'planned_end_date',
        'actual_end_date',

        # Geographic Information
        'recipient_country_code',
        'recipient_country_name',
        'recipient_region_code',
        'recipient_region_name',

        # Sector Information
        'sector_code',
        'sector_name',
        'sector_vocabulary',
        'sector_percentage',

        # Participating Organizations
        'participating_org_funding_ref',
        'participating_org_funding_name',
        'participating_org_funding_type',
        'participating_org_implementing_ref',
        'participating_org_implementing_name',
        'participating_org_implementing_type',

        # Budget Information
        'budget_type',
        'budget_status',
        'budget_period_start',
        'budget_period_end',
        'budget_value',
        'budget_currency',
        'budget_value_date',

        # Transaction Information (latest/main transaction)
        'transaction_type',
        'transaction_date',
        'transaction_value',
        'transaction_currency',
        'transaction_value_date',
        'transaction_description',
        'transaction_provider_org',
        'transaction_receiver_org',

        # Contact Information
        'contact_type',
        'contact_organisation',
        'contact_person_name',
        'contact_telephone',
        'contact_email',
        'contact_website',

        # Location Information
        'location_name',
        'location_description',
        'location_coordinates',
        'location_country_code',
        'location_administrative_code',

        # Document Links (main document)
        'document_url',
        'document_title',
        'document_format',
        'document_category',
        'document_language',

        # Results Information (simplified - main result)
        'result_type',
        'result_title',
        'result_description',

        # Additional fields for complex data (JSON strings)
        'additional_participating_orgs',  # JSON array of additional orgs
        'additional_budgets',  # JSON array of additional budgets
        'additional_transactions',  # JSON array of additional transactions
        'additional_sectors',  # JSON array of additional sectors
        'additional_locations',  # JSON array of additional locations
        'additional_documents',  # JSON array of additional documents
        'additional_results',  # JSON array of additional results
    ]

    def __init__(self):
        self.xml_generator = IatiXmlGenerator()

    def xml_to_csv(
        self,
        xml_input: Union[str, Path],
        csv_output: Union[str, Path],
        flatten_complex_data: bool = True,
        include_additional_fields: bool = True
    ) -> None:
        """
        Convert IATI XML file to CSV format.

        Args:
            xml_input: Path to input XML file or XML string
            csv_output: Path to output CSV file
            flatten_complex_data: If True, include main values in standard columns
            include_additional_fields: If True, include JSON fields for complex data
        """
        # Parse XML
        if isinstance(xml_input, (str, Path)) and Path(xml_input).exists():
            tree = ET.parse(xml_input)
            root = tree.getroot()
        else:
            # Assume it's an XML string
            root = ET.fromstring(str(xml_input))

        # Extract activities
        activities_data = []
        for activity_elem in root.findall('.//iati-activity'):
            activity_data = self._extract_activity_from_xml(
                activity_elem,
                flatten_complex_data,
                include_additional_fields
            )
            activities_data.append(activity_data)

        # Write to CSV
        self._write_csv(activities_data, csv_output)

    def csv_to_xml(
        self,
        csv_input: Union[str, Path],
        xml_output: Union[str, Path],
        validate_output: bool = True
    ) -> bool:
        """
        Convert CSV file to IATI XML format.

        Args:
            csv_input: Path to input CSV file
            xml_output: Path to output XML file
            validate_output: If True, validate the generated XML

        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            # Read CSV data
            activities = self._read_csv_and_create_activities(csv_input)

            # Create IATI activities container
            iati_activities = IatiActivities(
                version="2.03",
                generated_datetime=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                activities=activities
            )

            # Generate and save XML
            self.xml_generator.save_to_file(iati_activities, xml_output)

            # Validate if requested
            if validate_output:
                from .iati_schema_validator import IatiValidator
                validator = IatiValidator()
                xml_string = self.xml_generator.generate_iati_activities_xml(iati_activities)
                is_valid, errors = validator.validate(xml_string)

                if not is_valid:
                    print(f"Warning: Generated XML has validation errors: {errors}")
                    return False

            return True

        except Exception as e:
            print(f"Error converting CSV to XML: {e}")
            return False

    def generate_csv_template(
        self,
        output_path: Union[str, Path],
        include_examples: bool = True,
        format_type: str = 'basic'
    ) -> None:
        """
        Generate a CSV template file for data entry.

        Args:
            output_path: Path where to save the template
            include_examples: If True, include example rows
            format_type: 'basic' for essential fields, 'full' for all fields
        """
        if format_type == 'basic':
            columns = self._get_basic_columns()
        else:
            columns = self.CSV_COLUMNS

        template_data = []

        if include_examples:
            # Add example rows
            template_data.extend(self._get_example_rows(columns))

        # Write template
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for row in template_data:
                writer.writerow(row)

    def _extract_activity_from_xml(
        self,
        activity_elem: ET.Element,
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> Dict[str, Any]:
        """Extract activity data from XML element into CSV row format."""
        data = {}

        # Basic activity information
        data['activity_identifier'] = activity_elem.find('iati-identifier')
        data['activity_identifier'] = data['activity_identifier'].text if data['activity_identifier'] is not None else ''

        data['default_currency'] = activity_elem.get('default-currency', '')
        data['humanitarian'] = activity_elem.get('humanitarian', '0')

        # Title
        title_elem = activity_elem.find('title/narrative')
        data['title'] = title_elem.text if title_elem is not None else ''

        # Description
        desc_elem = activity_elem.find('description[@type="1"]/narrative')
        if desc_elem is None:
            desc_elem = activity_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        # Activity status
        status_elem = activity_elem.find('activity-status')
        data['activity_status'] = status_elem.get('code') if status_elem is not None else ''

        # Reporting organization
        rep_org_elem = activity_elem.find('reporting-org')
        if rep_org_elem is not None:
            data['reporting_org_ref'] = rep_org_elem.get('ref', '')
            data['reporting_org_type'] = rep_org_elem.get('type', '')
            rep_org_name = rep_org_elem.find('narrative')
            data['reporting_org_name'] = rep_org_name.text if rep_org_name is not None else ''

        # Dates
        self._extract_dates(activity_elem, data)

        # Geographic information
        self._extract_geography(activity_elem, data, flatten_complex_data)

        # Sector information
        self._extract_sectors(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Participating organizations
        self._extract_participating_orgs(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Budget information
        self._extract_budgets(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Transaction information
        self._extract_transactions(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Contact information
        self._extract_contact_info(activity_elem, data)

        # Location information
        self._extract_locations(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Document links
        self._extract_documents(activity_elem, data, flatten_complex_data, include_additional_fields)

        # Results
        self._extract_results(activity_elem, data, flatten_complex_data, include_additional_fields)

        return data

    def _extract_dates(self, activity_elem: ET.Element, data: Dict[str, Any]) -> None:
        """Extract activity dates."""
        for date_elem in activity_elem.findall('activity-date'):
            date_type = date_elem.get('type')
            iso_date = date_elem.get('iso-date', '')

            if date_type == '1':  # Planned start
                data['planned_start_date'] = iso_date
            elif date_type == '2':  # Actual start
                data['actual_start_date'] = iso_date
            elif date_type == '3':  # Planned end
                data['planned_end_date'] = iso_date
            elif date_type == '4':  # Actual end
                data['actual_end_date'] = iso_date

    def _extract_geography(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool
    ) -> None:
        """Extract recipient country and region information."""
        # Recipient country (take first one for main columns)
        country_elem = activity_elem.find('recipient-country')
        if country_elem is not None:
            data['recipient_country_code'] = country_elem.get('code', '')
            country_name = country_elem.find('narrative')
            data['recipient_country_name'] = country_name.text if country_name is not None else ''

        # Recipient region (take first one for main columns)
        region_elem = activity_elem.find('recipient-region')
        if region_elem is not None:
            data['recipient_region_code'] = region_elem.get('code', '')
            region_name = region_elem.find('narrative')
            data['recipient_region_name'] = region_name.text if region_name is not None else ''

    def _extract_sectors(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract sector information."""
        sectors = activity_elem.findall('sector')

        if sectors and flatten_complex_data:
            # Use first sector for main columns
            first_sector = sectors[0]
            data['sector_code'] = first_sector.get('code', '')
            data['sector_vocabulary'] = first_sector.get('vocabulary', '1')
            data['sector_percentage'] = first_sector.get('percentage', '100')

            sector_name = first_sector.find('narrative')
            data['sector_name'] = sector_name.text if sector_name is not None else ''

        if include_additional_fields and len(sectors) > 1:
            # Store additional sectors as JSON
            additional_sectors = []
            for sector in sectors[1:]:
                sector_data = {
                    'code': sector.get('code', ''),
                    'vocabulary': sector.get('vocabulary', '1'),
                    'percentage': sector.get('percentage', ''),
                    'name': ''
                }
                sector_name = sector.find('narrative')
                if sector_name is not None:
                    sector_data['name'] = sector_name.text
                additional_sectors.append(sector_data)

            data['additional_sectors'] = json.dumps(additional_sectors) if additional_sectors else ''

    def _extract_participating_orgs(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract participating organization information."""
        participating_orgs = activity_elem.findall('participating-org')

        funding_orgs = []
        implementing_orgs = []
        other_orgs = []

        for org in participating_orgs:
            role = org.get('role', '')
            org_data = {
                'ref': org.get('ref', ''),
                'type': org.get('type', ''),
                'role': role,
                'name': ''
            }

            org_name = org.find('narrative')
            if org_name is not None:
                org_data['name'] = org_name.text

            if role == '1':  # Funding
                funding_orgs.append(org_data)
            elif role == '4':  # Implementing
                implementing_orgs.append(org_data)
            else:
                other_orgs.append(org_data)

        # Set main columns
        if funding_orgs and flatten_complex_data:
            data['participating_org_funding_ref'] = funding_orgs[0]['ref']
            data['participating_org_funding_name'] = funding_orgs[0]['name']
            data['participating_org_funding_type'] = funding_orgs[0]['type']

        if implementing_orgs and flatten_complex_data:
            data['participating_org_implementing_ref'] = implementing_orgs[0]['ref']
            data['participating_org_implementing_name'] = implementing_orgs[0]['name']
            data['participating_org_implementing_type'] = implementing_orgs[0]['type']

        # Additional organizations
        if include_additional_fields:
            additional_orgs = funding_orgs[1:] + implementing_orgs[1:] + other_orgs
            if additional_orgs:
                data['additional_participating_orgs'] = json.dumps(additional_orgs)

    def _extract_budgets(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract budget information."""
        budgets = activity_elem.findall('budget')

        if budgets and flatten_complex_data:
            # Use first budget for main columns
            first_budget = budgets[0]
            data['budget_type'] = first_budget.get('type', '')
            data['budget_status'] = first_budget.get('status', '')

            period_start = first_budget.find('period-start')
            data['budget_period_start'] = period_start.get('iso-date') if period_start is not None else ''

            period_end = first_budget.find('period-end')
            data['budget_period_end'] = period_end.get('iso-date') if period_end is not None else ''

            value_elem = first_budget.find('value')
            if value_elem is not None:
                data['budget_value'] = value_elem.text or ''
                data['budget_currency'] = value_elem.get('currency', '')
                data['budget_value_date'] = value_elem.get('value-date', '')

        if include_additional_fields and len(budgets) > 1:
            # Store additional budgets as JSON
            additional_budgets = []
            for budget in budgets[1:]:
                budget_data = {
                    'type': budget.get('type', ''),
                    'status': budget.get('status', ''),
                    'period_start': '',
                    'period_end': '',
                    'value': '',
                    'currency': '',
                    'value_date': ''
                }

                period_start = budget.find('period-start')
                if period_start is not None:
                    budget_data['period_start'] = period_start.get('iso-date', '')

                period_end = budget.find('period-end')
                if period_end is not None:
                    budget_data['period_end'] = period_end.get('iso-date', '')

                value_elem = budget.find('value')
                if value_elem is not None:
                    budget_data['value'] = value_elem.text or ''
                    budget_data['currency'] = value_elem.get('currency', '')
                    budget_data['value_date'] = value_elem.get('value-date', '')

                additional_budgets.append(budget_data)

            data['additional_budgets'] = json.dumps(additional_budgets) if additional_budgets else ''

    def _extract_transactions(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract transaction information."""
        transactions = activity_elem.findall('transaction')

        if transactions and flatten_complex_data:
            # Use latest transaction for main columns
            latest_transaction = transactions[-1]  # Assume last is latest

            trans_type = latest_transaction.find('transaction-type')
            data['transaction_type'] = trans_type.get('code') if trans_type is not None else ''

            trans_date = latest_transaction.find('transaction-date')
            data['transaction_date'] = trans_date.get('iso-date') if trans_date is not None else ''

            value_elem = latest_transaction.find('value')
            if value_elem is not None:
                data['transaction_value'] = value_elem.text or ''
                data['transaction_currency'] = value_elem.get('currency', '')
                data['transaction_value_date'] = value_elem.get('value-date', '')

            desc_elem = latest_transaction.find('description/narrative')
            data['transaction_description'] = desc_elem.text if desc_elem is not None else ''

            provider_org = latest_transaction.find('provider-org/narrative')
            data['transaction_provider_org'] = provider_org.text if provider_org is not None else ''

            receiver_org = latest_transaction.find('receiver-org/narrative')
            data['transaction_receiver_org'] = receiver_org.text if receiver_org is not None else ''

        if include_additional_fields and len(transactions) > 1:
            # Store additional transactions as JSON
            additional_transactions = []
            for transaction in transactions[:-1]:  # All except the last one
                trans_data = {
                    'type': '',
                    'date': '',
                    'value': '',
                    'currency': '',
                    'value_date': '',
                    'description': '',
                    'provider_org': '',
                    'receiver_org': ''
                }

                trans_type = transaction.find('transaction-type')
                if trans_type is not None:
                    trans_data['type'] = trans_type.get('code', '')

                trans_date = transaction.find('transaction-date')
                if trans_date is not None:
                    trans_data['date'] = trans_date.get('iso-date', '')

                value_elem = transaction.find('value')
                if value_elem is not None:
                    trans_data['value'] = value_elem.text or ''
                    trans_data['currency'] = value_elem.get('currency', '')
                    trans_data['value_date'] = value_elem.get('value-date', '')

                desc_elem = transaction.find('description/narrative')
                if desc_elem is not None:
                    trans_data['description'] = desc_elem.text

                provider_org = transaction.find('provider-org/narrative')
                if provider_org is not None:
                    trans_data['provider_org'] = provider_org.text

                receiver_org = transaction.find('receiver-org/narrative')
                if receiver_org is not None:
                    trans_data['receiver_org'] = receiver_org.text

                additional_transactions.append(trans_data)

            data['additional_transactions'] = json.dumps(additional_transactions) if additional_transactions else ''

    def _extract_contact_info(self, activity_elem: ET.Element, data: Dict[str, Any]) -> None:
        """Extract contact information."""
        contact_elem = activity_elem.find('contact-info')
        if contact_elem is not None:
            data['contact_type'] = contact_elem.get('type', '')

            org_elem = contact_elem.find('organisation/narrative')
            data['contact_organisation'] = org_elem.text if org_elem is not None else ''

            person_elem = contact_elem.find('person-name/narrative')
            data['contact_person_name'] = person_elem.text if person_elem is not None else ''

            tel_elem = contact_elem.find('telephone')
            data['contact_telephone'] = tel_elem.text if tel_elem is not None else ''

            email_elem = contact_elem.find('email')
            data['contact_email'] = email_elem.text if email_elem is not None else ''

            website_elem = contact_elem.find('website')
            data['contact_website'] = website_elem.text if website_elem is not None else ''

    def _extract_locations(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract location information."""
        locations = activity_elem.findall('location')

        if locations and flatten_complex_data:
            # Use first location for main columns
            first_location = locations[0]

            name_elem = first_location.find('name/narrative')
            data['location_name'] = name_elem.text if name_elem is not None else ''

            desc_elem = first_location.find('description/narrative')
            data['location_description'] = desc_elem.text if desc_elem is not None else ''

            point_elem = first_location.find('point/pos')
            data['location_coordinates'] = point_elem.text if point_elem is not None else ''

            admin_elem = first_location.find('administrative')
            if admin_elem is not None:
                data['location_country_code'] = admin_elem.get('country', '')
                data['location_administrative_code'] = admin_elem.get('code', '')

    def _extract_documents(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract document link information."""
        documents = activity_elem.findall('document-link')

        if documents and flatten_complex_data:
            # Use first document for main columns
            first_doc = documents[0]
            data['document_url'] = first_doc.get('url', '')
            data['document_format'] = first_doc.get('format', '')

            title_elem = first_doc.find('title/narrative')
            data['document_title'] = title_elem.text if title_elem is not None else ''

            category_elem = first_doc.find('category')
            data['document_category'] = category_elem.get('code') if category_elem is not None else ''

            lang_elem = first_doc.find('language')
            data['document_language'] = lang_elem.get('code') if lang_elem is not None else ''

    def _extract_results(
        self,
        activity_elem: ET.Element,
        data: Dict[str, Any],
        flatten_complex_data: bool,
        include_additional_fields: bool
    ) -> None:
        """Extract results information."""
        results = activity_elem.findall('result')

        if results and flatten_complex_data:
            # Use first result for main columns
            first_result = results[0]
            data['result_type'] = first_result.get('type', '')

            title_elem = first_result.find('title/narrative')
            data['result_title'] = title_elem.text if title_elem is not None else ''

            desc_elem = first_result.find('description/narrative')
            data['result_description'] = desc_elem.text if desc_elem is not None else ''

    def _read_csv_and_create_activities(self, csv_input: Union[str, Path]) -> List[Activity]:
        """Read CSV file and convert to Activity objects."""
        activities = []

        with open(csv_input, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    activity = self._create_activity_from_row(row)
                    activities.append(activity)
                except Exception as e:
                    print(f"Error processing row {reader.line_num}: {e}")
                    continue

        return activities

    def _create_activity_from_row(self, row: Dict[str, str]) -> Activity:
        """Convert a CSV row into an Activity object."""
        # Basic activity information
        activity = Activity(
            iati_identifier=row['activity_identifier'],
            reporting_org=OrganizationRef(
                ref=row.get('reporting_org_ref', ''),
                type=row.get('reporting_org_type', ''),
                narratives=[Narrative(text=row.get('reporting_org_name', ''))]
            ),
            title=[Narrative(text=row['title'])],
            description=[{
                "type": "1",
                "narratives": [Narrative(text=row['description'])]
            }],
            activity_status=ActivityStatus(
                int(row['activity_status'])
            ) if row.get('activity_status') else ActivityStatus.IMPLEMENTATION,
            default_currency=row.get('default_currency', 'USD'),
            humanitarian=row.get('humanitarian', '0') == '1'
        )

        # Add dates
        self._add_dates_from_row(activity, row)

        # Add geographic information
        self._add_geography_from_row(activity, row)

        # Add sectors
        self._add_sectors_from_row(activity, row)

        # Add participating organizations
        self._add_participating_orgs_from_row(activity, row)

        # Add budgets
        self._add_budgets_from_row(activity, row)

        # Add transactions
        self._add_transactions_from_row(activity, row)

        # Add contact info
        self._add_contact_info_from_row(activity, row)

        # Add locations
        self._add_locations_from_row(activity, row)

        # Add documents
        self._add_documents_from_row(activity, row)

        # Add results
        self._add_results_from_row(activity, row)

        return activity

    def _add_dates_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add activity dates from CSV row."""
        if row.get('planned_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_START,
                iso_date=row['planned_start_date']
            ))

        if row.get('actual_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_START,
                iso_date=row['actual_start_date']
            ))

        if row.get('planned_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_END,
                iso_date=row['planned_end_date']
            ))

        if row.get('actual_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_END,
                iso_date=row['actual_end_date']
            ))

    def _add_geography_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add geographic information from CSV row."""
        if row.get('recipient_country_code'):
            country_data = {"code": row['recipient_country_code'], "percentage": 100}
            if row.get('recipient_country_name'):
                country_data["narratives"] = [Narrative(text=row['recipient_country_name'])]
            activity.recipient_countries.append(country_data)

        elif row.get('recipient_region_code'):
            region_data = {"code": row['recipient_region_code'], "percentage": 100}
            if row.get('recipient_region_name'):
                region_data["narratives"] = [Narrative(text=row['recipient_region_name'])]
            activity.recipient_regions.append(region_data)

    def _add_sectors_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add sector information from CSV row."""
        if row.get('sector_code'):
            sector_data = {
                "code": row['sector_code'],
                "vocabulary": row.get('sector_vocabulary', '1'),
                "percentage": int(row.get('sector_percentage', 100))
            }
            if row.get('sector_name'):
                sector_data["narratives"] = [Narrative(text=row['sector_name'])]
            activity.sectors.append(sector_data)

        # Add additional sectors from JSON field
        if row.get('additional_sectors'):
            try:
                additional_sectors = json.loads(row['additional_sectors'])
                for sector_data in additional_sectors:
                    sector = {
                        "code": sector_data.get('code', ''),
                        "vocabulary": sector_data.get('vocabulary', '1'),
                        "percentage": int(sector_data.get('percentage', 100))
                    }
                    if sector_data.get('name'):
                        sector["narratives"] = [Narrative(text=sector_data['name'])]
                    activity.sectors.append(sector)
            except (json.JSONDecodeError, ValueError):
                pass

    def _add_participating_orgs_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add participating organizations from CSV row."""
        # Funding organization
        if row.get('participating_org_funding_name'):
            activity.participating_orgs.append(ParticipatingOrg(
                role=OrganisationRole.FUNDING,
                ref=row.get('participating_org_funding_ref', ''),
                type=row.get('participating_org_funding_type', ''),
                narratives=[Narrative(text=row['participating_org_funding_name'])]
            ))

        # Implementing organization
        if row.get('participating_org_implementing_name'):
            activity.participating_orgs.append(ParticipatingOrg(
                role=OrganisationRole.IMPLEMENTING,
                ref=row.get('participating_org_implementing_ref', ''),
                type=row.get('participating_org_implementing_type', ''),
                narratives=[Narrative(text=row['participating_org_implementing_name'])]
            ))

        # Additional organizations from JSON field
        if row.get('additional_participating_orgs'):
            try:
                additional_orgs = json.loads(row['additional_participating_orgs'])
                for org_data in additional_orgs:
                    role_code = org_data.get('role', '1')
                    try:
                        role = OrganisationRole(role_code)
                    except ValueError:
                        role = role_code

                    activity.participating_orgs.append(ParticipatingOrg(
                        role=role,
                        ref=org_data.get('ref', ''),
                        type=org_data.get('type', ''),
                        narratives=[Narrative(text=org_data.get('name', ''))]
                    ))
            except (json.JSONDecodeError, ValueError):
                pass

    def _add_budgets_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add budget information from CSV row."""
        if row.get('budget_value'):
            activity.budgets.append(Budget(
                type=BudgetType(row.get('budget_type', '1')),
                status=BudgetStatus(row.get('budget_status', '1')),
                period_start=row['budget_period_start'],
                period_end=row['budget_period_end'],
                value=float(row['budget_value']),
                currency=row.get('budget_currency', row.get('default_currency', 'USD')),
                value_date=row.get('budget_value_date', row.get('budget_period_start'))
            ))

    def _add_transactions_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add transaction information from CSV row."""
        if row.get('transaction_value'):
            transaction_args = {
                'type': TransactionType(row.get('transaction_type', '2')),
                'date': row['transaction_date'],
                'value': float(row['transaction_value']),
                'currency': row.get('transaction_currency', row.get('default_currency', 'USD')),
                'value_date': row.get('transaction_value_date', row.get('transaction_date'))
            }

            if row.get('transaction_description'):
                transaction_args['description'] = [Narrative(text=row['transaction_description'])]

            activity.transactions.append(Transaction(**transaction_args))

    def _add_contact_info_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add contact information from CSV row."""
        if any(row.get(f'contact_{field}') for field in ['organisation', 'person_name', 'telephone', 'email', 'website']):
            contact_args = {}

            if row.get('contact_type'):
                contact_args['type'] = ContactType(row['contact_type'])

            if row.get('contact_organisation'):
                contact_args['organisation'] = [Narrative(text=row['contact_organisation'])]

            if row.get('contact_person_name'):
                contact_args['person_name'] = [Narrative(text=row['contact_person_name'])]

            if row.get('contact_telephone'):
                contact_args['telephone'] = row['contact_telephone']

            if row.get('contact_email'):
                contact_args['email'] = row['contact_email']

            if row.get('contact_website'):
                contact_args['website'] = row['contact_website']

            activity.contact_info = ContactInfo(**contact_args)

    def _add_locations_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add location information from CSV row."""
        if row.get('location_name'):
            location_args = {
                'name': [Narrative(text=row['location_name'])]
            }

            if row.get('location_description'):
                location_args['description'] = [Narrative(text=row['location_description'])]

            if row.get('location_coordinates'):
                coords = row['location_coordinates'].split(',')
                if len(coords) == 2:
                    location_args['point'] = {
                        'srsName': 'http://www.opengis.net/def/crs/EPSG/0/4326',
                        'pos': f"{coords[0].strip()} {coords[1].strip()}"
                    }

            if row.get('location_administrative_code'):
                location_args['administrative'] = [{
                    'code': row['location_administrative_code'],
                    'country': row.get('location_country_code', ''),
                    'vocabulary': 'G1',
                    'level': '1'
                }]

            activity.locations.append(Location(**location_args))

    def _add_documents_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add document link information from CSV row."""
        if row.get('document_url'):
            doc_args = {
                'url': row['document_url'],
                'format': row.get('document_format', 'application/pdf')
            }

            if row.get('document_title'):
                doc_args['title'] = [Narrative(text=row['document_title'])]

            if row.get('document_category'):
                doc_args['categories'] = [DocumentCategory(row['document_category'])]

            if row.get('document_language'):
                doc_args['languages'] = [row['document_language']]

            activity.document_links.append(DocumentLink(**doc_args))

    def _add_results_from_row(self, activity: Activity, row: Dict[str, str]) -> None:
        """Add results information from CSV row."""
        if row.get('result_title'):
            result_args = {
                'type': row.get('result_type', '1'),
                'title': [Narrative(text=row['result_title'])]
            }

            if row.get('result_description'):
                result_args['description'] = [Narrative(text=row['result_description'])]

            activity.results.append(Result(**result_args))

    def _write_csv(self, data: List[Dict[str, Any]], output_path: Union[str, Path]) -> None:
        """Write data to CSV file."""
        if not data:
            return

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)
            writer.writeheader()

            for row in data:
                # Ensure all columns are present
                clean_row = {col: row.get(col, '') for col in self.CSV_COLUMNS}
                writer.writerow(clean_row)

    def _get_basic_columns(self) -> List[str]:
        """Get list of basic/essential CSV columns."""
        return [
            'activity_identifier', 'title', 'description', 'activity_status',
            'default_currency', 'reporting_org_ref', 'reporting_org_name', 'reporting_org_type',
            'planned_start_date', 'actual_start_date', 'planned_end_date', 'actual_end_date',
            'recipient_country_code', 'recipient_country_name', 'recipient_region_code',
            'sector_code', 'sector_name', 'sector_percentage',
            'participating_org_funding_name', 'participating_org_implementing_name',
            'budget_period_start', 'budget_period_end', 'budget_value',
            'transaction_type', 'transaction_date', 'transaction_value', 'transaction_description'
        ]

    def _get_example_rows(self, columns: List[str]) -> List[Dict[str, str]]:
        """Generate example rows for template."""
        examples = [
            {
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'title': 'Rural Road Infrastructure Development Project',
                'description': (
                    'This project aims to improve rural connectivity and market access through the rehabilitation and '
                    'upgrading of 150km of rural roads in southeastern Costa Rica.'
                ),
                'activity_status': '2',
                'default_currency': 'USD',
                'reporting_org_ref': 'XM-DAC-46002',
                'reporting_org_name': 'Central American Bank for Economic Integration',
                'reporting_org_type': '40',
                'planned_start_date': '2023-01-15',
                'actual_start_date': '2023-02-01',
                'planned_end_date': '2025-12-31',
                'recipient_country_code': 'CR',
                'recipient_country_name': 'Costa Rica',
                'sector_code': '21020',
                'sector_name': 'Road transport',
                'sector_percentage': '100',
                'participating_org_funding_name': 'Central American Bank for Economic Integration',
                'participating_org_implementing_name': 'Ministry of Public Works and Transportation, Costa Rica',
                'budget_period_start': '2023-01-15',
                'budget_period_end': '2023-11-20',
                'budget_value': '25000000',
                'transaction_type': '2',
                'transaction_date': '2023-02-05',
                'transaction_value': '5000000',
                'transaction_description': 'Initial disbursement for preliminary studies and design',
                'result_title': 'Improved travel time reduced by 40% on target routes',
                'result_type': '2'
            }
        ]

        # Return only columns that exist in the requested column list
        return [{col: example.get(col, '') for col in columns} for example in examples]

    def to_dataframe(self, xml_input: Union[str, Path]):
        """
        Convert IATI XML to pandas DataFrame for analysis.

        Args:
            xml_input: Path to XML file or XML string

        Returns:
            pandas DataFrame with IATI activity data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame operations. Install with: pip install pandas")

        activities_data = []

        # Parse XML
        if isinstance(xml_input, (str, Path)) and Path(xml_input).exists():
            tree = ET.parse(xml_input)
            root = tree.getroot()
        else:
            root = ET.fromstring(str(xml_input))

        # Extract activities
        for activity_elem in root.findall('.//iati-activity'):
            activity_data = self._extract_activity_from_xml(activity_elem, True, True)
            activities_data.append(activity_data)

        # Convert to DataFrame
        df = pd.DataFrame(activities_data)

        # Clean up empty columns
        df = df.dropna(axis=1, how='all')

        return df

    def from_dataframe(self, df, xml_output: Union[str, Path]) -> bool:
        """
        Convert pandas DataFrame to IATI XML.

        Args:
            df: pandas DataFrame with IATI activity data
            xml_output: Path to output XML file

        Returns:
            True if conversion was successful
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame operations. Install with: pip install pandas")

        try:
            activities = []

            for _, row in df.iterrows():
                activity = self._create_activity_from_row(row.to_dict())
                activities.append(activity)

            # Create IATI activities container
            iati_activities = IatiActivities(
                version="2.03",
                generated_datetime=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                activities=activities
            )

            # Generate and save XML
            self.xml_generator.save_to_file(iati_activities, xml_output)
            return True

        except Exception as e:
            print(f"Error converting DataFrame to XML: {e}")
            return False
