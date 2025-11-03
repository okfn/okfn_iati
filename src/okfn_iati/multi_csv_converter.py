"""
IATI Multi-CSV Converter - Convert between IATI XML and multiple related CSV files.

This module provides a more structured approach to CSV conversion by splitting
IATI data into multiple related CSV files that preserve the hierarchical structure
while remaining user-friendly for editing in Excel or other tools.
"""

import csv
import shutil
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
from datetime import datetime

from .models import (
    Activity, Narrative, OrganizationRef, ParticipatingOrg, ActivityDate,
    Location, DocumentLink, Budget, Transaction, Result, IatiActivities, ContactInfo,
    Indicator, IndicatorBaseline, IndicatorPeriod, IndicatorPeriodTarget, IndicatorPeriodActual
)
from .enums import (
    ActivityStatus, ActivityDateType,
    DocumentCategory, ActivityScope,
    CollaborationType
)
from .xml_generator import IatiXmlGenerator


class IatiMultiCsvConverter:
    """
    Multi-CSV converter for IATI data.

    This converter creates/reads multiple CSV files to represent IATI activities:
    - activities.csv: Main activity information
    - participating_orgs.csv: Organizations participating in activities
    - budgets.csv: Budget information
    - transactions.csv: Financial transactions
    - locations.csv: Geographic locations
    - sectors.csv: Sector classifications
    - documents.csv: Document links
    - results.csv: Results and indicators
    - contact_info.csv: Contact information
    """

    def __init__(self):
        self.xml_generator = IatiXmlGenerator()

        # Define CSV file structure
        self.csv_files = {
            'activities': {
                'filename': 'activities.csv',
                'columns': [
                    'activity_identifier',  # Primary key
                    'title',
                    'description',
                    'activity_status',
                    'activity_scope',
                    'default_currency',
                    'humanitarian',
                    'hierarchy',
                    'last_updated_datetime',
                    'xml_lang',
                    'reporting_org_ref',
                    'reporting_org_name',
                    'reporting_org_type',
                    'planned_start_date',
                    'actual_start_date',
                    'planned_end_date',
                    'actual_end_date',
                    'recipient_country_code',
                    'recipient_country_name',
                    'recipient_region_code',
                    'recipient_region_name',
                    'collaboration_type',
                    'default_flow_type',
                    'default_finance_type',
                    'default_aid_type',
                    'default_tied_status'
                ]
            },
            'participating_orgs': {
                'filename': 'participating_orgs.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'org_ref',
                    'org_name',
                    'org_type',
                    'role',
                    'activity_id',
                    'crs_channel_code'
                ]
            },
            'sectors': {
                'filename': 'sectors.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'sector_code',
                    'sector_name',
                    'vocabulary',
                    'vocabulary_uri',
                    'percentage'
                ]
            },
            'budgets': {
                'filename': 'budgets.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'budget_type',
                    'budget_status',
                    'period_start',
                    'period_end',
                    'value',
                    'currency',
                    'value_date'
                ]
            },
            'transactions': {
                'filename': 'transactions.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'transaction_ref',
                    'transaction_type',
                    'transaction_date',
                    'value',
                    'currency',
                    'value_date',
                    'description',
                    'provider_org_ref',
                    'provider_org_name',
                    'provider_org_type',
                    'receiver_org_ref',
                    'receiver_org_name',
                    'receiver_org_type',
                    'receiver_org_activity_id',
                    'disbursement_channel',
                    'flow_type',
                    'finance_type',
                    'aid_type',
                    'tied_status',
                    'humanitarian',
                    'recipient_region'
                ]
            },
            'transaction_sectors': {
                'filename': 'transaction_sectors.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'transaction_ref',  # Foreign key to transactions
                    'sector_code',
                    'sector_name',
                    'vocabulary',
                    'vocabulary_uri'
                ]
            },
            'locations': {
                'filename': 'locations.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'location_ref',
                    'location_reach',
                    'location_id_vocabulary',
                    'location_id_code',
                    'name',
                    'description',
                    'activity_description',
                    'latitude',
                    'longitude',
                    'exactness',
                    'location_class',
                    'feature_designation',
                    'administrative_vocabulary',
                    'administrative_level',
                    'administrative_code',
                    'administrative_country'
                ]
            },
            'documents': {
                'filename': 'documents.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'url',
                    'format',
                    'title',
                    'description',
                    'category_code',
                    'language_code',
                    'document_date'
                ]
            },
            'results': {
                'filename': 'results.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'result_ref',
                    'result_type',
                    'aggregation_status',
                    'title',
                    'description'
                ]
            },
            'indicators': {
                'filename': 'indicators.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'result_ref',  # Foreign key to results
                    'indicator_ref',
                    'indicator_measure',
                    'ascending',
                    'aggregation_status',
                    'title',
                    'description',
                    'baseline_year',
                    'baseline_iso_date',
                    'baseline_value',
                    'baseline_comment'
                ]
            },
            'indicator_periods': {
                'filename': 'indicator_periods.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'result_ref',  # Foreign key to results
                    'indicator_ref',  # Foreign key to indicators
                    'period_start',
                    'period_end',
                    'target_value',
                    'target_comment',
                    'actual_value',
                    'actual_comment'
                ]
            },
            'activity_date': {
                'filename': 'activity_date.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'type',
                    'iso_date',
                    'narrative',
                    'narrative_lang'
                ]
            },
            'contact_info': {
                'filename': 'contact_info.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'contact_type',
                    'organisation',
                    'department',
                    'person_name',
                    'job_title',
                    'telephone',
                    'email',
                    'website',
                    'mailing_address'
                ]
            }
        }

    def xml_to_csv_folder(
        self,
        xml_input: Union[str, Path],
        csv_folder: Union[str, Path],
        overwrite: bool = True
    ) -> bool:
        """
        Convert IATI XML file to multiple CSV files in a folder.

        Args:
            xml_input: Path to input XML file or XML string
            csv_folder: Path to output folder for CSV files
            overwrite: If True, overwrite existing folder

        Returns:
            True if conversion was successful
        """
        csv_folder = Path(csv_folder)

        # Create or clean output folder
        if csv_folder.exists() and overwrite:
            shutil.rmtree(csv_folder)
        csv_folder.mkdir(parents=True, exist_ok=True)

        try:
            # Parse XML
            if isinstance(xml_input, (str, Path)) and Path(xml_input).exists():
                tree = ET.parse(xml_input)
                root = tree.getroot()
            else:
                root = ET.fromstring(str(xml_input))

            # Initialize data collections
            data_collections = {key: [] for key in self.csv_files.keys()}

            # Extract data from each activity
            for activity_elem in root.findall('.//iati-activity'):
                self._extract_activity_to_collections(activity_elem, data_collections)

            # Write each CSV file
            for csv_type, csv_config in self.csv_files.items():
                csv_path = csv_folder / csv_config['filename']
                self._write_csv_file(csv_path, csv_config['columns'], data_collections[csv_type])

            # Create a summary file
            self._create_summary_file(csv_folder, data_collections)

            print(f"✅ Successfully converted XML to CSV files in: {csv_folder}")
            return True

        except Exception as e:
            print(f"❌ Error converting XML to CSV: {e}")
            return False

    def csv_folder_to_xml(
        self,
        csv_folder: Union[str, Path],
        xml_output: Union[str, Path],
        validate_output: bool = True
    ) -> bool:
        """
        Convert multiple CSV files in a folder to IATI XML.

        Args:
            csv_folder: Path to folder containing CSV files
            xml_output: Path to output XML file
            validate_output: If True, validate the generated XML

        Returns:
            True if conversion was successful
        """
        csv_folder = Path(csv_folder)

        if not csv_folder.exists():
            print(f"❌ Error: CSV folder does not exist: {csv_folder}")
            return False

        try:
            # Read all CSV files
            data_collections = {}
            for csv_type, csv_config in self.csv_files.items():
                csv_path = csv_folder / csv_config['filename']
                if csv_path.exists():
                    data_collections[csv_type] = self._read_csv_file(csv_path)
                else:
                    data_collections[csv_type] = []

            # Convert to activities
            activities = self._build_activities_from_collections(data_collections)

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
                    print(f"⚠️  Warning: Generated XML has validation errors: {errors}")
                    return False

            print(f"✅ Successfully converted CSV files to XML: {xml_output}")
            return True

        except Exception as e:
            print(f"❌ Error converting CSV to XML: {e}")
            return False

    def generate_csv_templates(
        self,
        output_folder: Union[str, Path],
        include_examples: bool = True,
        csv_files: Optional[List[str]] = None
    ) -> None:
        """
        Generate CSV template files in a folder.

        Args:
            output_folder: Path where to save template files
            include_examples: If True, include example rows
            csv_files: List of specific CSV file types to generate (default: all)
        """
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        if csv_files is None:
            csv_files = list(self.csv_files.keys())

        for csv_type in csv_files:
            if csv_type not in self.csv_files:
                continue

            csv_config = self.csv_files[csv_type]
            csv_path = output_folder / csv_config['filename']

            # Create template data
            template_data = []
            if include_examples:
                template_data = self._get_example_data(csv_type)

            # Write template
            self._write_csv_file(csv_path, csv_config['columns'], template_data)

        # Create README with instructions
        self._create_readme_file(output_folder)

        print(f"✅ Generated CSV templates in: {output_folder}")

    def _extract_activity_to_collections(
        self,
        activity_elem: ET.Element,
        data_collections: Dict[str, List[Dict]]
    ) -> None:
        """Extract activity data into separate collections."""
        activity_id = self._get_activity_identifier(activity_elem)

        # Extract main activity data
        activity_data = self._extract_main_activity_data(activity_elem, activity_id)
        data_collections['activities'].append(activity_data)

        # Extract participating organizations
        for org_elem in activity_elem.findall('participating-org'):
            org_data = self._extract_participating_org_data(org_elem, activity_id)
            data_collections['participating_orgs'].append(org_data)

        # Extract sectors
        for sector_elem in activity_elem.findall('sector'):
            sector_data = self._extract_sector_data(sector_elem, activity_id)
            data_collections['sectors'].append(sector_data)

        # Extract budgets
        for budget_elem in activity_elem.findall('budget'):
            budget_data = self._extract_budget_data(budget_elem, activity_id)
            data_collections['budgets'].append(budget_data)

        # Extract transactions
        for trans_elem in activity_elem.findall('transaction'):
            trans_data = self._extract_transaction_data(trans_elem, activity_id)
            data_collections['transactions'].append(trans_data)

            # Extract transaction sectors
            transaction_ref = trans_data.get('transaction_ref', '')
            for sector_elem in trans_elem.findall('sector'):
                sector_data = self._extract_transaction_sector_data(
                    sector_elem,
                    activity_id,
                    transaction_ref
                )
                data_collections['transaction_sectors'].append(sector_data)

        # Extract locations
        for location_elem in activity_elem.findall('location'):
            location_data = self._extract_location_data(location_elem, activity_id)
            data_collections['locations'].append(location_data)

        # Extract documents
        for doc_elem in activity_elem.findall('document-link'):
            doc_data = self._extract_document_data(doc_elem, activity_id)
            data_collections['documents'].append(doc_data)

        # Extract results and indicators
        result_index = 0
        for result_elem in activity_elem.findall('result'):
            result_index += 1
            result_data = self._extract_result_data(
                result_elem,
                activity_id,
                result_index
            )
            data_collections['results'].append(result_data)

            # Extract indicators for this result
            indicator_index = 0
            for indicator_elem in result_elem.findall('indicator'):
                indicator_index += 1
                indicator_data = self._extract_indicator_data(
                    indicator_elem,
                    activity_id,
                    result_data['result_ref'],
                    indicator_index
                )
                data_collections['indicators'].append(indicator_data)

                # Extract periods for this indicator
                indicator_ref = indicator_data.get('indicator_ref', '')
                for period_elem in indicator_elem.findall('period'):
                    period_data = self._extract_indicator_period_data(
                        period_elem,
                        activity_id,
                        result_data.get('result_ref', ''),
                        indicator_ref
                    )
                    data_collections['indicator_periods'].append(period_data)

        # Extract activity dates
        for date_elem in activity_elem.findall('activity-date'):
            date_data = self._extract_activity_date_data(date_elem, activity_id)
            data_collections['activity_date'].append(date_data)

        # Extract contact info
        contact_elem = activity_elem.find('contact-info')
        if contact_elem is not None:
            contact_data = self._extract_contact_data(contact_elem, activity_id)
            data_collections['contact_info'].append(contact_data)

    def _get_activity_identifier(self, activity_elem: ET.Element) -> str:
        """Get activity identifier from XML element."""
        id_elem = activity_elem.find('iati-identifier')
        return id_elem.text if id_elem is not None else ''

    def _extract_indicator_period_data(
        self,
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
            data['target_comment'] = target_comment.text if target_comment is not None else ''
        else:
            data['target_value'] = ''
            data['target_comment'] = ''

        # Actual
        actual_elem = period_elem.find('actual')
        if actual_elem is not None:
            data['actual_value'] = actual_elem.get('value', '')
            actual_comment = actual_elem.find('comment/narrative')
            data['actual_comment'] = actual_comment.text if actual_comment is not None else ''
        else:
            data['actual_value'] = ''
            data['actual_comment'] = ''

        return data

    def _extract_transaction_sector_data(
        self,
        sector_elem: ET.Element,
        activity_id: str,
        transaction_ref: str
    ) -> Dict[str, str]:
        """Extract transaction sector data."""
        data = {
            'activity_identifier': activity_id,
            'transaction_ref': transaction_ref
        }

        data['sector_code'] = sector_elem.get('code', '')
        data['vocabulary'] = sector_elem.get('vocabulary', '1')
        data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')

        sector_name = sector_elem.find('narrative')
        data['sector_name'] = sector_name.text if sector_name is not None else ''

        return data

    def _extract_main_activity_data(self, activity_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract main activity information."""
        data = {'activity_identifier': activity_id}

        # Basic attributes
        data['default_currency'] = activity_elem.get('default-currency', '')
        data['humanitarian'] = activity_elem.get('humanitarian', '0')
        data['hierarchy'] = activity_elem.get('hierarchy', '1')
        data['last_updated_datetime'] = activity_elem.get('last-updated-datetime', '')
        data['xml_lang'] = activity_elem.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')

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

        # Activity scope
        scope_elem = activity_elem.find('activity-scope')
        data['activity_scope'] = scope_elem.get('code') if scope_elem is not None else ''

        # Reporting organization
        rep_org_elem = activity_elem.find('reporting-org')
        if rep_org_elem is not None:
            data['reporting_org_ref'] = rep_org_elem.get('ref', '')
            data['reporting_org_type'] = rep_org_elem.get('type', '')
            rep_org_name = rep_org_elem.find('narrative')
            data['reporting_org_name'] = rep_org_name.text if rep_org_name is not None else ''
        else:
            data['reporting_org_ref'] = ''
            data['reporting_org_type'] = ''
            data['reporting_org_name'] = ''

        # Recipient country (first one only for main table)
        country_elem = activity_elem.find('recipient-country')
        if country_elem is not None:
            data['recipient_country_code'] = country_elem.get('code', '')
            country_name = country_elem.find('narrative')
            data['recipient_country_name'] = country_name.text if country_name is not None else ''
        else:
            data['recipient_country_code'] = ''
            data['recipient_country_name'] = ''

        # Recipient region (first one only for main table)
        region_elem = activity_elem.find('recipient-region')
        if region_elem is not None:
            data['recipient_region_code'] = region_elem.get('code', '')
            region_name = region_elem.find('narrative')
            data['recipient_region_name'] = region_name.text if region_name is not None else ''
        else:
            data['recipient_region_code'] = ''
            data['recipient_region_name'] = ''

        # Default flow/finance/aid/tied status and collaboration type
        collab_elem = activity_elem.find('collaboration-type')
        data['collaboration_type'] = collab_elem.get('code') if collab_elem is not None else ''

        flow_elem = activity_elem.find('default-flow-type')
        data['default_flow_type'] = flow_elem.get('code') if flow_elem is not None else ''

        finance_elem = activity_elem.find('default-finance-type')
        data['default_finance_type'] = finance_elem.get('code') if finance_elem is not None else ''

        aid_elem = activity_elem.find('default-aid-type')
        data['default_aid_type'] = aid_elem.get('code') if aid_elem is not None else ''

        tied_elem = activity_elem.find('default-tied-status')
        data['default_tied_status'] = tied_elem.get('code') if tied_elem is not None else ''

        # Fill in empty values for missing columns
        for col in self.csv_files['activities']['columns']:
            if col not in data:
                data[col] = ''

        return data

    def _extract_participating_org_data(self, org_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract participating organization data."""
        data = {'activity_identifier': activity_id}

        data['org_ref'] = org_elem.get('ref', '')
        data['org_type'] = org_elem.get('type', '')
        data['role'] = org_elem.get('role', '')
        data['activity_id'] = org_elem.get('activity-id', '')
        data['crs_channel_code'] = org_elem.get('crs-channel-code', '')

        org_name = org_elem.find('narrative')
        data['org_name'] = org_name.text if org_name is not None else ''

        return data

    def _extract_sector_data(self, sector_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract sector data."""
        data = {'activity_identifier': activity_id}

        data['sector_code'] = sector_elem.get('code', '')
        data['vocabulary'] = sector_elem.get('vocabulary', '1')
        data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')
        data['percentage'] = sector_elem.get('percentage', '100')

        sector_name = sector_elem.find('narrative')
        data['sector_name'] = sector_name.text if sector_name is not None else ''

        return data

    def _extract_budget_data(self, budget_elem: ET.Element, activity_id: str) -> Dict[str, str]:
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
            data['value'] = value_elem.text or ''
            data['currency'] = value_elem.get('currency', '')
            data['value_date'] = value_elem.get('value-date', '')
        else:
            data['value'] = ''
            data['currency'] = ''
            data['value_date'] = ''

        return data

    def _extract_transaction_data(self, trans_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract transaction data."""
        data = {'activity_identifier': activity_id}

        data['transaction_ref'] = trans_elem.get('ref', '')
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
            data['value'] = value_elem.text or ''
            data['currency'] = value_elem.get('currency', '')
            data['value_date'] = value_elem.get('value-date', '')
        else:
            data['value'] = ''
            data['currency'] = ''
            data['value_date'] = ''

        # Description
        desc_elem = trans_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        # Provider org
        provider_elem = trans_elem.find('provider-org')
        if provider_elem is not None:
            data['provider_org_ref'] = provider_elem.get('ref', '')
            data['provider_org_type'] = provider_elem.get('type', '')
            provider_name = provider_elem.find('narrative')
            data['provider_org_name'] = provider_name.text if provider_name is not None else ''
        else:
            data['provider_org_ref'] = ''
            data['provider_org_type'] = ''
            data['provider_org_name'] = ''

        # Receiver org
        receiver_elem = trans_elem.find('receiver-org')
        if receiver_elem is not None:
            data['receiver_org_ref'] = receiver_elem.get('ref', '')
            data['receiver_org_type'] = receiver_elem.get('type', '')
            data['receiver_org_activity_id'] = receiver_elem.get('receiver-activity-id', '')
            receiver_name = receiver_elem.find('narrative')
            data['receiver_org_name'] = receiver_name.text if receiver_name is not None else ''
        else:
            data['receiver_org_ref'] = ''
            data['receiver_org_type'] = ''
            data['receiver_org_name'] = ''
            data['receiver_org_activity_id'] = ''

        # Additional fields
        data['disbursement_channel'] = ''
        data['flow_type'] = ''
        data['finance_type'] = ''
        data['aid_type'] = ''
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

        tied_status_elem = trans_elem.find('tied-status')
        if tied_status_elem is not None:
            data['tied_status'] = tied_status_elem.get('code') if tied_status_elem.get('code') != '0' else ''

        recipient_region_elem = trans_elem.find('recipient-region')
        if recipient_region_elem is not None:
            data['recipient_region'] = recipient_region_elem.get('code', '')

        return data

    def _extract_location_data(self, location_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract location data."""
        data = {'activity_identifier': activity_id}

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
        data['name'] = name_elem.text if name_elem is not None else ''

        desc_elem = location_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        activity_desc_elem = location_elem.find('activity-description/narrative')
        data['activity_description'] = activity_desc_elem.text if activity_desc_elem is not None else ''

        # Coordinates
        point_elem = location_elem.find('point/pos')
        if point_elem is not None and point_elem.text:
            coords = point_elem.text.split()
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

    def _extract_document_data(self, doc_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract document data."""
        data = {'activity_identifier': activity_id}

        data['url'] = doc_elem.get('url', '')
        data['format'] = doc_elem.get('format', '')
        data['document_date'] = doc_elem.get('document-date', '')

        title_elem = doc_elem.find('title/narrative')
        data['title'] = title_elem.text if title_elem is not None else ''

        desc_elem = doc_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        category_elem = doc_elem.find('category')
        data['category_code'] = category_elem.get('code') if category_elem is not None else ''

        lang_elem = doc_elem.find('language')
        data['language_code'] = lang_elem.get('code') if lang_elem is not None else ''

        return data

    def _extract_result_data(
        self,
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
        data['title'] = title_elem.text if title_elem is not None else ''

        desc_elem = result_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        return data

    def _extract_indicator_data(
        self,
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
            if narrative is not None and narrative.text:
                data['title'] = narrative.text.strip()

        # Description
        desc_elem = indicator_elem.find('description')
        if desc_elem is not None:
            narrative = desc_elem.find('narrative')
            if narrative is not None and narrative.text:
                data['description'] = narrative.text.strip()

        # Baseline
        baseline_elem = indicator_elem.find('baseline')
        if baseline_elem is not None:
            data['baseline_year'] = baseline_elem.get('year', '')
            data['baseline_iso_date'] = baseline_elem.get('iso-date', '')
            data['baseline_value'] = baseline_elem.get('value', '')

            comment = baseline_elem.find('comment/narrative')
            if comment is not None and comment.text:
                data['baseline_comment'] = comment.text.strip()

        return data

    def _extract_contact_data(self, contact_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract contact information data."""
        data = {'activity_identifier': activity_id}

        data['contact_type'] = contact_elem.get('type', '')

        org_elem = contact_elem.find('organisation/narrative')
        data['organisation'] = org_elem.text if org_elem is not None else ''

        dept_elem = contact_elem.find('department/narrative')
        data['department'] = dept_elem.text if dept_elem is not None else ''

        person_elem = contact_elem.find('person-name/narrative')
        data['person_name'] = person_elem.text if person_elem is not None else ''

        job_elem = contact_elem.find('job-title/narrative')
        data['job_title'] = job_elem.text if job_elem is not None else ''

        tel_elem = contact_elem.find('telephone')
        data['telephone'] = tel_elem.text if tel_elem is not None else ''

        email_elem = contact_elem.find('email')
        data['email'] = email_elem.text if email_elem is not None else ''

        website_elem = contact_elem.find('website')
        data['website'] = website_elem.text if website_elem is not None else ''

        addr_elem = contact_elem.find('mailing-address/narrative')
        data['mailing_address'] = addr_elem.text if addr_elem is not None else ''

        return data

    def _extract_activity_date_data(self, date_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract activity date data."""
        data = {'activity_identifier': activity_id}

        data['type'] = date_elem.get('type')
        iso_date = date_elem.get('iso-date', '')
        data['iso_date'] = iso_date

        # Get narrative if exists (it's optional)
        narrative = date_elem.find('narrative')
        if narrative is not None:
            data['narrative'] = narrative.text or ''
            data['narrative_lang'] = narrative.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        else:
            data['narrative'] = ''
            data['narrative_lang'] = ''

        return data

    def _write_csv_file(self, file_path: Path, columns: List[str], data: List[Dict[str, str]]) -> None:
        """Write data to CSV file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for row in data:
                # Ensure all columns are present
                clean_row = {col: row.get(col, '') for col in columns}
                writer.writerow(clean_row)

    def _read_csv_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Read data from CSV file."""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data

    def _build_activities_from_collections(self, data_collections: Dict[str, List[Dict]]) -> List[Activity]:
        """Build Activity objects from CSV data collections."""
        activities = []

        # Group data by activity identifier
        activity_data_map = {}

        for activity_row in data_collections.get('activities', []):
            activity_id = activity_row['activity_identifier']
            if not activity_id:
                continue

            activity_data_map[activity_id] = {
                'main': activity_row,
                'participating_orgs': [],
                'sectors': [],
                'budgets': [],
                'transactions': [],
                'transaction_sectors': [],
                'locations': [],
                'documents': [],
                'results': [],
                'indicators': [],
                'indicator_periods': [],
                'activity_date': [],
                'contact_info': []
            }

        # Group related data
        for csv_type in [
            'participating_orgs', 'sectors', 'budgets', 'transactions',
            'transaction_sectors', 'locations', 'documents', 'results', 'indicators', 'indicator_periods',
            'activity_date', 'contact_info'
        ]:
            for row in data_collections.get(csv_type, []):
                activity_id = row.get('activity_identifier')
                if activity_id in activity_data_map:
                    activity_data_map[activity_id][csv_type].append(row)

        # Build activities
        for activity_id, data in activity_data_map.items():
            try:
                activity = self._build_activity_from_data(data)
                activities.append(activity)
            except Exception as e:
                print(f"Error building activity {activity_id}: {e}\n\nSELF {self} {type(self)}\n\t Data: {data}")
                raise

        return activities

    def _build_activity_from_data(self, data: Dict[str, Any]) -> Activity:
        """Build an Activity object from grouped data."""
        main_data = data['main']

        # Create basic activity
        activity = Activity(
            iati_identifier=main_data['activity_identifier'],
            reporting_org=OrganizationRef(
                ref=main_data.get('reporting_org_ref', ''),
                type=main_data.get('reporting_org_type', ''),
                narratives=[
                    Narrative(text=main_data.get('reporting_org_name', ''))
                ] if main_data.get('reporting_org_name') else []
            ),
            title=[Narrative(text=main_data.get('title', ''))] if main_data.get('title') else [],
            description=[{
                "type": "1",
                "narratives": [Narrative(text=main_data.get('description', ''))]
            }] if main_data.get('description') else [],
            activity_status=self._parse_activity_status(main_data.get('activity_status')),
            default_currency=main_data.get('default_currency', 'USD'),
            humanitarian=main_data.get('humanitarian', '0') == '1',
            hierarchy=main_data.get('hierarchy', '1'),
            last_updated_datetime=main_data.get('last_updated_datetime'),
            xml_lang=main_data.get('xml_lang', 'en'),
            activity_scope=self._parse_activity_scope(main_data.get('activity_scope'))
        )

        # Add dates
        self._add_dates_from_main_data(activity, main_data)

        # Add geographic information
        self._add_geography_from_main_data(activity, main_data)

        # Add default types from main data
        self._add_default_types_from_main_data(activity, main_data)

        # Add participating organizations
        for org_data in data['participating_orgs']:
            activity.participating_orgs.append(self._build_participating_org(org_data))

        # Add sectors
        for sector_data in data['sectors']:
            activity.sectors.append(self._build_sector(sector_data))

        # Add budgets
        for budget_data in data['budgets']:
            activity.budgets.append(self._build_budget(budget_data))

        # Add transactions
        for trans_data in data['transactions']:
            trans_ref = trans_data.get('transaction_ref')
            transaction_sectors_data = [
                row for row in data.get('transaction_sectors', [])
                if row.get('transaction_ref') == trans_ref and row.get('activity_identifier') == activity.iati_identifier
            ]
            activity.transactions.append(self._build_transaction(trans_data, transaction_sectors_data))

        # Add locations
        for location_data in data['locations']:
            activity.locations.append(self._build_location(location_data))

        # Add documents
        for doc_data in data['documents']:
            activity.document_links.append(self._build_document(doc_data))

        # Add activity_dates
        for date_data in data['activity_date']:
            activity.activity_dates.append(self._build_activity_date(date_data))

        # Add contact info
        for contact_data in data['contact_info']:
            activity.contact_info = self._build_contact_info(contact_data)
            break  # Only one contact info per activity

        # Add results with indicators
        for result_data in data['results']:
            result_ref = result_data.get('result_ref', '')

            # Get indicators for this result
            result_indicators = [
                ind for ind in data['indicators']
                if ind.get('result_ref') == result_ref
            ]

            # Get periods for this result's indicators
            result_periods = [
                period for period in data['indicator_periods']
                if period.get('result_ref') == result_ref
            ]

            # Build result with indicators
            result = self._build_result_with_indicators(
                result_data,
                result_indicators,
                result_periods
            )

            activity.results.append(result)

        return activity

    def _build_activity_date(self, date_data: Dict[str, str]) -> ActivityDate:
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

    def _parse_activity_status(self, status_code: str) -> Optional[ActivityStatus]:
        """Parse activity status code to enum."""
        if not status_code:
            return None
        try:
            return ActivityStatus(int(status_code))
        except (ValueError, TypeError):
            return None

    def _parse_activity_scope(self, scope_code: str) -> Optional[ActivityScope]:
        """Parse activity scope code to enum."""
        if not scope_code:
            return None
        try:
            return ActivityScope(scope_code)
        except (ValueError, TypeError):
            return None

    def _add_dates_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
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

    def _add_geography_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
        """Add recipient countries and regions from main data."""
        # Add recipient country if present
        country_code = main_data.get('recipient_country_code')
        if country_code:
            country_data = {
                'code': country_code,
                'percentage': 100
            }
            country_name = main_data.get('recipient_country_name')
            if country_name:
                country_data['narratives'] = [Narrative(text=country_name)]

            activity.recipient_countries.append(country_data)

        # Add recipient region if present
        region_code = main_data.get('recipient_region_code')
        if region_code:
            region_data = {
                'code': region_code,
                'percentage': 100
            }
            region_name = main_data.get('recipient_region_name')
            if region_name:
                region_data['narratives'] = [Narrative(text=region_name)]

            activity.recipient_regions.append(region_data)

    def _add_default_types_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
        """Add default flow/finance/aid/tied status from main data as activity-level attributes."""
        # Note: These are stored as activity attributes in IATI, not as separate elements
        # They would be used when creating transactions or other elements if not specified

        # Add collaboration type if present
        collaboration_type = main_data.get('collaboration_type')
        if collaboration_type:
            try:
                activity.collaboration_type = CollaborationType(collaboration_type)
            except (ValueError, TypeError):
                pass  # Skip invalid collaboration type

        # Store default types for use in transactions (if not overridden)
        # Note: These are not standard Activity model attributes, but we'll store them as custom attributes
        if hasattr(activity, '__dict__'):
            activity.__dict__['default_flow_type'] = main_data.get('default_flow_type')
            activity.__dict__['default_finance_type'] = main_data.get('default_finance_type')
            activity.__dict__['default_aid_type'] = main_data.get('default_aid_type')
            activity.__dict__['default_tied_status'] = main_data.get('default_tied_status')

    def _build_participating_org(self, org_data: Dict[str, str]) -> ParticipatingOrg:
        """Build ParticipatingOrg from data."""
        return ParticipatingOrg(
            role=org_data.get('role', '1'),
            ref=org_data.get('org_ref', ''),
            type=org_data.get('org_type', ''),
            activity_id=org_data.get('activity_id'),
            crs_channel_code=org_data.get('crs_channel_code'),
            narratives=[Narrative(text=org_data.get('org_name', ''))] if org_data.get('org_name') else []
        )

    def _build_sector(self, sector_data: Dict[str, str]) -> Dict[str, Any]:
        """Build sector from data."""
        sector = {
            "code": sector_data.get('sector_code', ''),
            "vocabulary": sector_data.get('vocabulary', '1')
        }

        if sector_data.get('vocabulary_uri'):
            sector["vocabulary_uri"] = sector_data['vocabulary_uri']

        if sector_data.get('percentage'):
            try:
                sector["percentage"] = float(sector_data['percentage'])
            except (ValueError, TypeError):
                sector["percentage"] = 100.0
        else:
            sector["percentage"] = 100.0

        if sector_data.get('sector_name'):
            sector["narratives"] = [Narrative(text=sector_data['sector_name'])]

        return sector

    def _build_budget(self, budget_data: Dict[str, str]) -> Budget:
        """Build Budget from data."""
        return Budget(
            type=budget_data.get('budget_type', '1'),
            status=budget_data.get('budget_status', '1'),
            period_start=budget_data.get('period_start', ''),
            period_end=budget_data.get('period_end', ''),
            value=float(budget_data.get('value', 0)) if budget_data.get('value') else 0.0,
            currency=budget_data.get('currency', 'USD'),
            value_date=budget_data.get('value_date', '')
        )

    def _build_transaction(
        self,
        trans_data: Dict[str, str],
        trans_sectors: Optional[List[Dict[str, str]]] = None
    ) -> Transaction:
        """Build Transaction from data."""
        transaction_args = {
            'type': trans_data.get('transaction_type', '2'),
            'date': trans_data.get('transaction_date', ''),
            'value': float(trans_data.get('value', 0)) if trans_data.get('value') else 0.0,
            'currency': trans_data.get('currency', 'USD'),
            'value_date': trans_data.get('value_date', ''),
            'transaction_ref': trans_data.get('transaction_ref')
        }

        if trans_data.get('description'):
            transaction_args['description'] = [Narrative(text=trans_data['description'])]

        # Add provider org
        if trans_data.get('provider_org_ref') or trans_data.get('provider_org_name'):
            transaction_args['provider_org'] = OrganizationRef(
                ref=trans_data.get('provider_org_ref', ''),
                type=trans_data.get('provider_org_type', ''),
                narratives=[
                    Narrative(text=trans_data.get('provider_org_name', ''))
                ] if trans_data.get('provider_org_name') else [],
                receiver_org_activity_id=trans_data.get('receiver_org_activity_id', ''),
            )

        # Add receiver org
        if trans_data.get('receiver_org_ref') or trans_data.get('receiver_org_name'):
            transaction_args['receiver_org'] = OrganizationRef(
                ref=trans_data.get('receiver_org_ref', ''),
                type=trans_data.get('receiver_org_type', ''),
                narratives=[
                    Narrative(text=trans_data.get('receiver_org_name', ''))
                ] if trans_data.get('receiver_org_name') else [],
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
            transaction_args['aid_type'] = {"code": trans_data['aid_type']}
        if trans_data.get('recipient_region'):
            transaction_args['recipient_region'] = trans_data['recipient_region']

        if trans_sectors:
            sectors = []
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

    def _build_location(self, location_data: Dict[str, str]) -> Location:
        """Build Location from data."""
        location_args = {}

        if location_data.get('name'):
            location_args['name'] = [Narrative(text=location_data['name'])]

        if location_data.get('description'):
            location_args['description'] = [Narrative(text=location_data['description'])]

        if location_data.get('latitude') and location_data.get('longitude'):
            location_args['point'] = {
                'srsName': 'http://www.opengis.net/def/crs/EPSG/0/4326',
                'pos': f"{location_data['latitude']} {location_data['longitude']}"
            }

        return Location(**location_args)

    def _build_document(self, doc_data: Dict[str, str]) -> DocumentLink:
        """Build DocumentLink from data."""
        doc_args = {
            'url': doc_data.get('url', ''),
            'format': doc_data.get('format', 'application/pdf')
        }

        if doc_data.get('title'):
            doc_args['title'] = [Narrative(text=doc_data['title'])]

        if doc_data.get('category_code'):
            doc_args['categories'] = [DocumentCategory(doc_data['category_code'])]

        return DocumentLink(**doc_args)

    def _build_contact_info(self, contact_data: Dict[str, str]) -> ContactInfo:
        """Build ContactInfo from data."""
        contact_args = {}

        if contact_data.get('contact_type'):
            contact_args['type'] = contact_data['contact_type']
        if contact_data.get('organisation'):
            contact_args['organisation'] = [Narrative(text=contact_data['organisation'])]
        if contact_data.get('department'):
            contact_args['department'] = [Narrative(text=contact_data['department'])]
        if contact_data.get('person_name'):
            contact_args['person_name'] = [Narrative(text=contact_data['person_name'])]
        if contact_data.get('job_title'):
            contact_args['job_title'] = [Narrative(text=contact_data['job_title'])]
        if contact_data.get('telephone'):
            contact_args['telephone'] = contact_data['telephone']
        if contact_data.get('email'):
            contact_args['email'] = contact_data['email']
        if contact_data.get('website'):
            contact_args['website'] = contact_data['website']
        if contact_data.get('mailing_address'):
            contact_args['mailing_address'] = [Narrative(text=contact_data['mailing_address'])]

        return ContactInfo(**contact_args)

    def _build_result_with_indicators(
        self,
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
            indicator = self._build_indicator(indicator_data)

            # Add periods to this indicator
            indicator_ref = indicator_data.get('indicator_ref', '')
            for period_data in periods_data:
                if period_data.get('indicator_ref') == indicator_ref:
                    period = self._build_indicator_period(period_data)
                    if indicator.period is None:
                        indicator.period = []
                    indicator.period.append(period)

            indicators.append(indicator)

        result_args['indicator'] = indicators
        return Result(**result_args)

    def _build_indicator(self, indicator_data: Dict[str, str]) -> Indicator:
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

    def _build_indicator_period(self, period_data: Dict[str, str]) -> IndicatorPeriod:
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

    def _get_example_data(self, csv_type: str) -> List[Dict[str, str]]:
        """Get example data for CSV templates."""
        if csv_type == 'activities':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'title': 'Rural Road Infrastructure Development Project',
                'description': (
                    'This project aims to improve rural connectivity and market access through the rehabilitation and '
                    'upgrading of 150km of rural roads in southeastern Costa Rica.'
                ),
                'activity_status': '2',
                'activity_scope': '4',  # National
                'default_currency': 'USD',
                'humanitarian': '0',
                'hierarchy': '1',
                'xml_lang': 'en',
                'reporting_org_ref': 'XM-DAC-46002',
                'reporting_org_name': 'Central American Bank for Economic Integration',
                'reporting_org_type': '40',
                'planned_start_date': '2023-01-15',
                'actual_start_date': '2023-02-01',
                'planned_end_date': '2025-12-31',
                'recipient_country_code': 'CR',
                'recipient_country_name': 'Costa Rica',
                'collaboration_type': '1',  # Bilateral
                'default_flow_type': '10',  # ODA
                'default_finance_type': '110',  # Standard grant
                'default_aid_type': 'C01',  # Project-type interventions
                'default_tied_status': '5'  # Untied
            }]
        elif csv_type == 'participating_orgs':
            return [
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'org_ref': 'XM-DAC-46002',
                    'org_name': 'Central American Bank for Economic Integration',
                    'org_type': '40',
                    'role': '1'  # Funding
                },
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'org_ref': 'CR-MOPT',
                    'org_name': 'Ministry of Public Works and Transportation, Costa Rica',
                    'org_type': '10',
                    'role': '4'  # Implementing
                }
            ]
        elif csv_type == 'contact_info':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'contact_type': '1',  # General
                'organisation': 'Central American Bank for Economic Integration',
                'department': 'Infrastructure Projects Division',
                'person_name': 'Ana García',
                'job_title': 'Project Manager',
                'telephone': '+506-2123-4567',
                'email': 'ana.garcia@bcie.org',
                'website': 'https://www.bcie.org',
                'mailing_address': 'Tegucigalpa M.D.C., Honduras'
            }]
        elif csv_type == 'results':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'result_ref': 'result_1',
                'result_type': '1',  # Output
                'aggregation_status': 'true',
                'title': 'Improved rural road infrastructure',
                'description': 'Rural roads rehabilitated and upgraded to improve connectivity'
            }]
        # ...existing code for other examples...

        return []

    def _create_summary_file(self, csv_folder: Path, data_collections: Dict[str, List[Dict]]) -> None:
        """Create a summary file with statistics."""
        summary_path = csv_folder / 'summary.txt'

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("IATI CSV Conversion Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Conversion completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("Files created:\n")
            for csv_type, csv_config in self.csv_files.items():
                count = len(data_collections.get(csv_type, []))
                f.write(f"  {csv_config['filename']}: {count} records\n")

            f.write(f"\nTotal activities: {len(data_collections.get('activities', []))}\n")

    def _create_readme_file(self, output_folder: Path) -> None:
        """Create a README file with instructions."""
        readme_path = output_folder / 'README.md'

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""# IATI CSV Templates

This folder contains CSV templates for entering IATI activity data. Each CSV file represents a
different aspect of IATI activities:

## Files Description

- **activities.csv**: Main activity information (identifier, title, description, etc.)
- **participating_orgs.csv**: Organizations participating in activities
- **sectors.csv**: Sector classifications for activities
- **budgets.csv**: Budget information for activities
- **transactions.csv**: Financial transactions
- **locations.csv**: Geographic locations
- **documents.csv**: Document links
- **results.csv**: Results and outcomes
- **indicators.csv**: Indicators for results
- **contact_info.csv**: Contact information

## Key Relationships

- All files use `activity_identifier` to link data to specific activities
- The `activity_identifier` must match between files
- Results and indicators are linked via `result_ref`

## Usage Instructions

1. Start by filling out **activities.csv** with your main activity data
2. Add related data in other CSV files using the same `activity_identifier`
3. Use the conversion tool to generate IATI XML from these CSV files

## Important Notes

- The `activity_identifier` must be unique and follow IATI standards
- Dates should be in ISO format (YYYY-MM-DD)
- Use standard IATI code lists for codes (status, types, etc.)
- Empty fields are allowed but required fields should be filled

## Example Activity Identifier Format

`{organization-identifier}-{project-code}`

Example: `XM-DAC-46002-CR-2025`

""")


"""
Real life sample usage:

python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/CAF-ActivityFile-2025-10-10.xml data-samples/csv_folders/CAF
and roll back to test
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/CAF data-samples/xml/CAF-ActivityFile-2025-10-10-back.xml

python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/iadb-Brazil.xml data-samples/csv_folders/IADBBrasil
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/IADBBrasil data-samples/xml/iadb-Brazil-back.xml
 -> Error with activity dates (some activities do not include dates)
    Warning: Generated XML has validation errors:
    {'schema_errors':
    [
    "<string>:2241:0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT: Element 'contact-info': This element is not expected. Expected is ( activity-date ).",
    "<string>:15466:0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT: Element 'contact-info': This element is not expected. Expected is ( activity-date )."
    ...
    ]

python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/usaid-798.xml data-samples/csv_folders/usaid-798
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/usaid-798 data-samples/xml/usaid-798-back.xml
 -> Error Warning: Generated XML has validation errors:
 {
 'schema_errors':[],
 'ruleset_errors': [
   'Each activity must have either a sector element or all transactions must have sector elements',
   'Each activity must have either a sector element or all transactions must have sector elements',
   'Each activity must have either a sector element or all transactions must have sector elements',
   'Each activity must have either a sector element or all transactions must have sector elements',
   'Each activity must have either a sector element or all transactions must have sector elements'
]
"""
