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
    Location, DocumentLink, Budget, Transaction, Result, IatiActivities, ContactInfo
)
from .enums import (
    ActivityStatus, ActivityDateType, TransactionType, BudgetType, BudgetStatus,
    OrganisationRole, ContactType, DocumentCategory
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
                    'disbursement_channel',
                    'flow_type',
                    'finance_type',
                    'aid_type',
                    'tied_status',
                    'humanitarian'
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
                    'baseline_value',
                    'baseline_comment'
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

        # Extract locations
        for location_elem in activity_elem.findall('location'):
            location_data = self._extract_location_data(location_elem, activity_id)
            data_collections['locations'].append(location_data)

        # Extract documents
        for doc_elem in activity_elem.findall('document-link'):
            doc_data = self._extract_document_data(doc_elem, activity_id)
            data_collections['documents'].append(doc_data)

        # Extract results and indicators
        for result_elem in activity_elem.findall('result'):
            result_data = self._extract_result_data(result_elem, activity_id)
            data_collections['results'].append(result_data)

            # Extract indicators for this result
            for indicator_elem in result_elem.findall('indicator'):
                indicator_data = self._extract_indicator_data(indicator_elem, activity_id, result_data.get('result_ref', ''))
                data_collections['indicators'].append(indicator_data)

        # Extract contact info
        contact_elem = activity_elem.find('contact-info')
        if contact_elem is not None:
            contact_data = self._extract_contact_data(contact_elem, activity_id)
            data_collections['contact_info'].append(contact_data)

    def _get_activity_identifier(self, activity_elem: ET.Element) -> str:
        """Get activity identifier from XML element."""
        id_elem = activity_elem.find('iati-identifier')
        return id_elem.text if id_elem is not None else ''

    def _extract_main_activity_data(self, activity_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract main activity information."""
        data = {'activity_identifier': activity_id}

        # Basic attributes
        data['activity_status'] = ''
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

        # Dates
        for date_elem in activity_elem.findall('activity-date'):
            date_type = date_elem.get('type')
            iso_date = date_elem.get('iso-date', '')

            if date_type == '1':
                data['planned_start_date'] = iso_date
            elif date_type == '2':
                data['actual_start_date'] = iso_date
            elif date_type == '3':
                data['planned_end_date'] = iso_date
            elif date_type == '4':
                data['actual_end_date'] = iso_date

        # Recipient country (first one only for main table)
        country_elem = activity_elem.find('recipient-country')
        if country_elem is not None:
            data['recipient_country_code'] = country_elem.get('code', '')
            country_name = country_elem.find('narrative')
            data['recipient_country_name'] = country_name.text if country_name is not None else ''

        # Recipient region (first one only for main table)
        region_elem = activity_elem.find('recipient-region')
        if region_elem is not None:
            data['recipient_region_code'] = region_elem.get('code', '')
            region_name = region_elem.find('narrative')
            data['recipient_region_name'] = region_name.text if region_name is not None else ''

        # Default flow/finance/aid/tied status
        data['collaboration_type'] = ''
        data['default_flow_type'] = ''
        data['default_finance_type'] = ''
        data['default_aid_type'] = ''
        data['default_tied_status'] = ''

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
        data['humanitarian'] = trans_elem.get('humanitarian', '0')

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
            receiver_name = receiver_elem.find('narrative')
            data['receiver_org_name'] = receiver_name.text if receiver_name is not None else ''
        else:
            data['receiver_org_ref'] = ''
            data['receiver_org_type'] = ''
            data['receiver_org_name'] = ''

        # Additional fields
        data['disbursement_channel'] = ''
        data['flow_type'] = ''
        data['finance_type'] = ''
        data['aid_type'] = ''
        data['tied_status'] = ''

        # Extract additional transaction elements
        flow_type_elem = trans_elem.find('flow-type')
        if flow_type_elem is not None:
            data['flow_type'] = flow_type_elem.get('code', '')

        finance_type_elem = trans_elem.find('finance-type')
        if finance_type_elem is not None:
            data['finance_type'] = finance_type_elem.get('code', '')

        aid_type_elem = trans_elem.find('aid-type')
        if aid_type_elem is not None:
            data['aid_type'] = aid_type_elem.get('code', '')

        tied_status_elem = trans_elem.find('tied-status')
        if tied_status_elem is not None:
            data['tied_status'] = tied_status_elem.get('code', '')

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

    def _extract_result_data(self, result_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract result data."""
        data = {'activity_identifier': activity_id}

        data['result_ref'] = result_elem.get('ref', f"result_{len(result_elem)}")
        data['result_type'] = result_elem.get('type', '')
        data['aggregation_status'] = result_elem.get('aggregation-status', '')

        title_elem = result_elem.find('title/narrative')
        data['title'] = title_elem.text if title_elem is not None else ''

        desc_elem = result_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        return data

    def _extract_indicator_data(self, indicator_elem: ET.Element, activity_id: str, result_ref: str) -> Dict[str, str]:
        """Extract indicator data."""
        data = {
            'activity_identifier': activity_id,
            'result_ref': result_ref
        }

        data['indicator_ref'] = indicator_elem.get('ref', f"indicator_{len(indicator_elem)}")
        data['indicator_measure'] = indicator_elem.get('measure', '')
        data['ascending'] = indicator_elem.get('ascending', '')
        data['aggregation_status'] = indicator_elem.get('aggregation-status', '')

        title_elem = indicator_elem.find('title/narrative')
        data['title'] = title_elem.text if title_elem is not None else ''

        desc_elem = indicator_elem.find('description/narrative')
        data['description'] = desc_elem.text if desc_elem is not None else ''

        # Baseline
        baseline_elem = indicator_elem.find('baseline')
        if baseline_elem is not None:
            data['baseline_year'] = baseline_elem.get('year', '')
            baseline_value = baseline_elem.find('value')
            data['baseline_value'] = baseline_value.text if baseline_value is not None else ''
            baseline_comment = baseline_elem.find('comment/narrative')
            data['baseline_comment'] = baseline_comment.text if baseline_comment is not None else ''
        else:
            data['baseline_year'] = ''
            data['baseline_value'] = ''
            data['baseline_comment'] = ''

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
                'locations': [],
                'documents': [],
                'results': [],
                'indicators': [],
                'contact_info': []
            }

        # Group related data
        for csv_type in [
            'participating_orgs', 'sectors', 'budgets', 'transactions',
            'locations', 'documents', 'results', 'indicators', 'contact_info'
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
                print(f"Error building activity {activity_id}: {e}")
                continue

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
                narratives=[Narrative(text=main_data.get('reporting_org_name', ''))]
            ),
            title=[Narrative(text=main_data.get('title', ''))],
            description=[{
                "type": "1",
                "narratives": [Narrative(text=main_data.get('description', ''))]
            }],
            activity_status=ActivityStatus(
                int(main_data['activity_status'])
            ) if main_data.get('activity_status') else ActivityStatus.IMPLEMENTATION,
            default_currency=main_data.get('default_currency', 'USD'),
            humanitarian=main_data.get('humanitarian', '0') == '1'
        )

        # Add dates
        self._add_dates_from_main_data(activity, main_data)

        # Add geographic information
        self._add_geography_from_main_data(activity, main_data)

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
            activity.transactions.append(self._build_transaction(trans_data))

        # Add locations
        for location_data in data['locations']:
            activity.locations.append(self._build_location(location_data))

        # Add documents
        for doc_data in data['documents']:
            activity.document_links.append(self._build_document(doc_data))

        # Add results
        for result_data in data['results']:
            activity.results.append(self._build_result(result_data))

        # Add contact info
        if data['contact_info']:
            activity.contact_info = self._build_contact_info(data['contact_info'][0])

        return activity

    def _add_dates_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
        """Add activity dates from main data."""
        if main_data.get('planned_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_START,
                iso_date=main_data['planned_start_date']
            ))

        if main_data.get('actual_start_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_START,
                iso_date=main_data['actual_start_date']
            ))

        if main_data.get('planned_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.PLANNED_END,
                iso_date=main_data['planned_end_date']
            ))

        if main_data.get('actual_end_date'):
            activity.activity_dates.append(ActivityDate(
                type=ActivityDateType.ACTUAL_END,
                iso_date=main_data['actual_end_date']
            ))

    def _add_geography_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
        """Add geographic information from main data."""
        if main_data.get('recipient_country_code'):
            country_data = {"code": main_data['recipient_country_code'], "percentage": 100}
            if main_data.get('recipient_country_name'):
                country_data["narratives"] = [Narrative(text=main_data['recipient_country_name'])]
            activity.recipient_countries.append(country_data)

        elif main_data.get('recipient_region_code'):
            region_data = {"code": main_data['recipient_region_code'], "percentage": 100}
            if main_data.get('recipient_region_name'):
                region_data["narratives"] = [Narrative(text=main_data['recipient_region_name'])]
            activity.recipient_regions.append(region_data)

    def _build_participating_org(self, org_data: Dict[str, str]) -> ParticipatingOrg:
        """Build ParticipatingOrg from data."""
        return ParticipatingOrg(
            role=OrganisationRole(org_data.get('role', '1')),
            ref=org_data.get('org_ref', ''),
            type=org_data.get('org_type', ''),
            narratives=[Narrative(text=org_data.get('org_name', ''))]
        )

    def _build_sector(self, sector_data: Dict[str, str]) -> Dict[str, Any]:
        """Build sector from data."""
        sector = {
            "code": sector_data.get('sector_code', ''),
            "vocabulary": sector_data.get('vocabulary', '1'),
            "percentage": int(sector_data.get('percentage', 100))
        }
        if sector_data.get('sector_name'):
            sector["narratives"] = [Narrative(text=sector_data['sector_name'])]
        return sector

    def _build_budget(self, budget_data: Dict[str, str]) -> Budget:
        """Build Budget from data."""
        return Budget(
            type=BudgetType(budget_data.get('budget_type', '1')),
            status=BudgetStatus(budget_data.get('budget_status', '1')),
            period_start=budget_data.get('period_start', ''),
            period_end=budget_data.get('period_end', ''),
            value=float(budget_data.get('value', 0)),
            currency=budget_data.get('currency', 'USD'),
            value_date=budget_data.get('value_date', '')
        )

    def _build_transaction(self, trans_data: Dict[str, str]) -> Transaction:
        """Build Transaction from data."""
        transaction_args = {
            'type': TransactionType(trans_data.get('transaction_type', '2')),
            'date': trans_data.get('transaction_date', ''),
            'value': float(trans_data.get('value', 0)),
            'currency': trans_data.get('currency', 'USD'),
            'value_date': trans_data.get('value_date', '')
        }

        if trans_data.get('description'):
            transaction_args['description'] = [Narrative(text=trans_data['description'])]

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

    def _build_result(self, result_data: Dict[str, str]) -> Result:
        """Build Result from data."""
        result_args = {
            'type': result_data.get('result_type', '1'),
            'title': [Narrative(text=result_data.get('title', ''))]
        }

        if result_data.get('description'):
            result_args['description'] = [Narrative(text=result_data['description'])]

        return Result(**result_args)

    def _build_contact_info(self, contact_data: Dict[str, str]) -> ContactInfo:
        """Build ContactInfo from data."""
        contact_args = {}

        if contact_data.get('contact_type'):
            contact_args['type'] = ContactType(contact_data['contact_type'])

        if contact_data.get('organisation'):
            contact_args['organisation'] = [Narrative(text=contact_data['organisation'])]

        if contact_data.get('person_name'):
            contact_args['person_name'] = [Narrative(text=contact_data['person_name'])]

        if contact_data.get('telephone'):
            contact_args['telephone'] = contact_data['telephone']

        if contact_data.get('email'):
            contact_args['email'] = contact_data['email']

        if contact_data.get('website'):
            contact_args['website'] = contact_data['website']

        return ContactInfo(**contact_args)

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
                'default_currency': 'USD',
                'reporting_org_ref': 'XM-DAC-46002',
                'reporting_org_name': 'Central American Bank for Economic Integration',
                'reporting_org_type': '40',
                'planned_start_date': '2023-01-15',
                'actual_start_date': '2023-02-01',
                'planned_end_date': '2025-12-31',
                'recipient_country_code': 'CR',
                'recipient_country_name': 'Costa Rica'
            }]
        elif csv_type == 'participating_orgs':
            return [
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'org_ref': 'XM-DAC-46002',
                    'org_name': 'Central American Bank for Economic Integration',
                    'org_type': '40',
                    'role': '1'
                },
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'org_ref': 'CR-MOPT',
                    'org_name': 'Ministry of Public Works and Transportation, Costa Rica',
                    'org_type': '10',
                    'role': '4'
                }
            ]
        elif csv_type == 'sectors':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'sector_code': '21020',
                'sector_name': 'Road transport',
                'vocabulary': '1',
                'percentage': '100'
            }]
        elif csv_type == 'budgets':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'budget_type': '1',
                'budget_status': '2',
                'period_start': '2023-01-15',
                'period_end': '2023-12-31',
                'value': '25000000',
                'currency': 'USD',
                'value_date': '2023-01-15'
            }]
        elif csv_type == 'transactions':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'transaction_type': '2',
                'transaction_date': '2023-02-05',
                'value': '5000000',
                'currency': 'USD',
                'value_date': '2023-02-05',
                'description': 'Initial disbursement for preliminary studies and design'
            }]

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

"""
