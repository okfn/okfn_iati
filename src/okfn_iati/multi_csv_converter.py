"""
IATI Multi-CSV Converter - Convert between IATI XML and multiple related CSV files.

This module provides a more structured approach to CSV conversion by splitting
IATI data into multiple related CSV files that preserve the hierarchical structure
while remaining user-friendly for editing in Excel or other tools.

LIMITATIONS:
- Custom namespace elements (e.g., USAID's usg:treasury-account) are NOT preserved
  during XML -> CSV -> XML conversion. These are organization-specific extensions
  that don't fit into the standard CSV structure.
- If you need to preserve custom elements, use XML-to-XML transformations instead.
"""

import csv
import shutil
import xml.etree.ElementTree as ET
import html
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
                    'title_lang',  # NEW: lang attribute for title narrative
                    'description',
                    'description_lang',  # NEW: lang attribute for description narrative
                    'activity_status',
                    'activity_scope',
                    'default_currency',
                    'humanitarian',
                    'hierarchy',
                    'last_updated_datetime',
                    'xml_lang',
                    'reporting_org_ref',
                    'reporting_org_name',
                    'reporting_org_name_lang',  # NEW: lang attribute for reporting org narrative
                    'reporting_org_type',
                    'reporting_org_secondary_reporter',
                    'planned_start_date',
                    'actual_start_date',
                    'planned_end_date',
                    'actual_end_date',
                    'recipient_country_code',
                    'recipient_country_percentage',
                    'recipient_country_name',
                    'recipient_country_lang',
                    'recipient_region_code',
                    'recipient_region_percentage',
                    'recipient_region_name',
                    'recipient_region_lang',
                    'collaboration_type',
                    'default_flow_type',
                    'default_finance_type',
                    'default_aid_type',
                    'default_tied_status',
                    'conditions_attached'
                ]
            },
            'participating_orgs': {
                'filename': 'participating_orgs.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'org_ref',
                    'org_name',
                    'org_name_lang',
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
                    'description_lang',
                    'provider_org_ref',
                    'provider_org_name',
                    'provider_org_lang',
                    'provider_org_type',
                    'receiver_org_ref',
                    'receiver_org_name',
                    'receiver_org_lang',
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
                    'transaction_type',  # NEW: transaction type code to uniquely identify transaction
                    'sector_code',
                    'sector_name',
                    'vocabulary',
                    'vocabulary_uri'
                ]
            },
            'locations': {
                'filename': 'locations.csv',
                'columns': [
                    'activity_identifier',
                    'location_ref',
                    'location_reach',
                    'location_id_vocabulary',
                    'location_id_code',
                    'name',
                    'name_lang',
                    'description',
                    'description_lang',
                    'activity_description',
                    'activity_description_lang',
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
                    'activity_identifier',
                    'url',
                    'format',
                    'title',
                    'title_lang',
                    'description',
                    'description_lang',
                    'category_code',
                    'language_code',
                    'document_date',
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
                    'activity_identifier',
                    'contact_type',
                    'organisation',
                    'organisation_lang',
                    'department',
                    'department_lang',
                    'person_name',
                    'person_name_lang',
                    'person_name_present',
                    'job_title',
                    'job_title_lang',
                    'telephone',
                    'email',
                    'email_present',
                    'website',
                    'mailing_address',
                    'mailing_address_lang'
                ]
            },
            'conditions': {
                'filename': 'conditions.csv',
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'condition_type',
                    'condition_text'
                ]
            },
            'descriptions': {
                'filename': 'descriptions.csv',
                'columns': [
                    'activity_identifier',
                    'description_type',
                    'description_sequence',
                    'narrative',
                    'narrative_lang',
                    'narrative_sequence'
                ]
            },
            'country_budget_items': {
                'filename': 'country_budget_items.csv',
                'columns': [
                    'activity_identifier',
                    'vocabulary',
                    'budget_item_code',
                    'budget_item_percentage',
                    'description',
                    'description_lang'
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

            # Extract root-level attributes
            root_attributes = {
                'linked_data_default': root.get('linked-data-default', '')
            }

            # Create a summary file with root attributes
            self._create_summary_file(csv_folder, data_collections, root_attributes)

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

            # Read root attributes from summary file if it exists
            linked_data_default = None
            summary_path = csv_folder / 'summary.txt'
            if summary_path.exists():
                with open(summary_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('linked_data_default:'):
                            linked_data_default = line.split(':', 1)[1].strip()
                            break

            # Create IATI activities container
            iati_activities = IatiActivities(
                version="2.03",
                generated_datetime=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                linked_data_default=linked_data_default,
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

    def _get_text_content(self, element: Optional[ET.Element]) -> str:
        """Get text content from element, unescaping HTML entities."""
        if element is None or not element.text:
            return ''
        return html.unescape(element.text)

    def _extract_activity_to_collections(  # noqa: C901
        self,
        activity_elem: ET.Element,
        data_collections: Dict[str, List[Dict]]
    ) -> None:
        """Extract activity data into separate collections."""
        activity_id = self._get_activity_identifier(activity_elem)

        # Extract main activity data
        activity_data = self._extract_main_activity_data(activity_elem, activity_id)
        data_collections['activities'].append(activity_data)

        # Extract descriptions
        description_index = 0
        for desc_elem in activity_elem.findall('description'):
            description_index += 1
            narratives = desc_elem.findall('narrative') or [None]
            for narrative_index, narrative_elem in enumerate(narratives, start=1):
                description_row = self._extract_description_data(
                    desc_elem,
                    activity_id,
                    description_index,
                    narrative_elem,
                    narrative_index
                )
                data_collections['descriptions'].append(description_row)

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

        # Extract transactions with deduplication
        seen_transaction_sectors = set()  # Track (activity_id, transaction_ref, transaction_type, sector_code, vocabulary)

        for trans_elem in activity_elem.findall('transaction'):
            trans_data = self._extract_transaction_data(trans_elem, activity_id)
            data_collections['transactions'].append(trans_data)

            # Extract transaction sectors with deduplication
            transaction_ref = trans_data.get('transaction_ref', '')
            transaction_type = trans_data.get('transaction_type', '')  # NEW: Get transaction type

            for sector_elem in trans_elem.findall('sector'):
                sector_data = self._extract_transaction_sector_data(
                    sector_elem,
                    activity_id,
                    transaction_ref,
                    transaction_type  # NEW: Pass transaction type
                )

                # Create unique key for this transaction sector
                sector_key = (
                    activity_id,
                    transaction_ref,
                    transaction_type,  # NEW: Include type in unique key
                    sector_data.get('sector_code', ''),
                    sector_data.get('vocabulary', '1')
                )

                # Only add if we haven't seen this exact combination before
                if sector_key not in seen_transaction_sectors:
                    seen_transaction_sectors.add(sector_key)
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

        # Extract conditions
        conditions_elem = activity_elem.find('conditions')
        if conditions_elem is not None:
            for condition_elem in conditions_elem.findall('condition'):
                condition_data = self._extract_condition_data(condition_elem, activity_id)
                data_collections['conditions'].append(condition_data)

        # Extract country budget items
        for cbi_elem in activity_elem.findall('country-budget-items'):
            data_collections['country_budget_items'].extend(
                self._extract_country_budget_items(cbi_elem, activity_id)
            )

    def _get_activity_identifier(self, activity_elem: ET.Element) -> str:
        """Get activity identifier from XML element."""
        id_elem = activity_elem.find('iati-identifier')
        return self._get_text_content(id_elem)

    def _extract_description_data(
        self,
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
            data['narrative'] = self._get_text_content(narrative_elem)
            data['narrative_lang'] = narrative_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        else:
            data['narrative'] = ''
            data['narrative_lang'] = ''

        return data

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
            data['target_comment'] = self._get_text_content(target_comment)
        else:
            data['target_value'] = ''
            data['target_comment'] = ''

        # Actual
        actual_elem = period_elem.find('actual')
        if actual_elem is not None:
            data['actual_value'] = actual_elem.get('value', '')
            actual_comment = actual_elem.find('comment/narrative')
            data['actual_comment'] = self._get_text_content(actual_comment)
        else:
            data['actual_value'] = ''
            data['actual_comment'] = ''

        return data

    def _extract_transaction_sector_data(
        self,
        sector_elem: ET.Element,
        activity_id: str,
        transaction_ref: str,
        transaction_type: str  # NEW: Add transaction_type parameter
    ) -> Dict[str, str]:
        """Extract transaction sector data."""
        data = {
            'activity_identifier': activity_id,
            'transaction_ref': transaction_ref,
            'transaction_type': transaction_type  # NEW: Include transaction type
        }

        data['sector_code'] = sector_elem.get('code', '')
        data['vocabulary'] = sector_elem.get('vocabulary', '1')
        data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')

        sector_name = sector_elem.find('narrative')
        data['sector_name'] = self._get_text_content(sector_name)

        return data

    def _extract_country_budget_items(
        self,
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
                data['description'] = self._get_text_content(desc_elem)
                data['description_lang'] = desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '')
            else:
                data['description'] = ''
                data['description_lang'] = ''

            items.append(data)

        return items

    def _extract_main_activity_data(self, activity_elem: ET.Element, activity_id: str) -> Dict[str, str]:
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
        data['title'] = self._get_text_content(title_elem)
        data['title_lang'] = title_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if title_elem is not None else ''

        # Description - extract lang attribute from narrative
        desc_elem = activity_elem.find('description[@type="1"]/narrative')
        if desc_elem is None:
            desc_elem = activity_elem.find('description/narrative')
        data['description'] = self._get_text_content(desc_elem)
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
            data['reporting_org_name'] = self._get_text_content(rep_org_name)
            data['reporting_org_name_lang'] = (
                rep_org_name.get('{http://www.w3.org/XML/1998/namespace}lang', '') if rep_org_name is not None else ''
            )
            data['reporting_org_secondary_reporter'] = rep_org_elem.get('secondary-reporter', '')
        else:
            data['reporting_org_ref'] = ''
            data['reporting_org_type'] = ''
            data['reporting_org_name'] = ''
            data['reporting_org_name_lang'] = ''
            data['reporting_org_secondary_reporter'] = ''

        # Recipient country (first one only for main table)
        country_elem = activity_elem.find('recipient-country')
        if country_elem is not None:
            data['recipient_country_code'] = country_elem.get('code', '')
            country_name = country_elem.find('narrative')
            data['recipient_country_name'] = self._get_text_content(country_name)
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
            data['recipient_region_name'] = self._get_text_content(region_name)
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

        tied_elem = activity_elem.find('default-tied-status')
        data['default_tied_status'] = tied_elem.get('code') if tied_elem is not None else ''

        # Conditions attached
        conditions_elem = activity_elem.find('conditions')
        data['conditions_attached'] = conditions_elem.get('attached', '') if conditions_elem is not None else ''

        # Fill in empty values for missing columns
        for col in self.csv_files['activities']['columns']:
            if col not in data:
                data[col] = ''

        return data

    def _extract_condition_data(self, condition_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract individual condition data."""
        data = {
            'activity_identifier': activity_id,
            'condition_type': condition_elem.get('type', ''),
            'condition_text': self._get_text_content(condition_elem.find('narrative'))
        }
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
        data['org_name'] = self._get_text_content(org_name)
        data['org_name_lang'] = (
            org_name.get('{http://www.w3.org/XML/1998/namespace}lang', '') if org_name is not None else ''
        )

        return data

    def _extract_sector_data(self, sector_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract sector data."""
        data = {'activity_identifier': activity_id}

        data['sector_code'] = sector_elem.get('code', '')
        data['vocabulary'] = sector_elem.get('vocabulary', '1')
        data['vocabulary_uri'] = sector_elem.get('vocabulary-uri', '')
        data['percentage'] = sector_elem.get('percentage', '')

        sector_name = sector_elem.find('narrative')
        data['sector_name'] = self._get_text_content(sector_name)

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
            data['value'] = self._get_text_content(value_elem)
            data['currency'] = value_elem.get('currency', '')
            data['value_date'] = value_elem.get('value-date', '')
        else:
            data['value'] = ''
            data['currency'] = ''
            data['value_date'] = ''

        return data

    def _extract_transaction_data(self, trans_elem: ET.Element, activity_id: str) -> Dict[str, str]:
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
            data['value'] = self._get_text_content(value_elem)
            data['currency'] = value_elem.get('currency', '')
            data['value_date'] = value_elem.get('value-date', '')
        else:
            data['value'] = ''
            data['currency'] = ''
            data['value_date'] = ''

        # Description
        desc_elem = trans_elem.find('description/narrative')
        data['description'] = self._get_text_content(desc_elem)
        data['description_lang'] = (
            desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if desc_elem is not None else ''
        )

        # Provider org
        provider_elem = trans_elem.find('provider-org')
        if provider_elem is not None:
            data['provider_org_ref'] = provider_elem.get('ref', '')
            data['provider_org_type'] = provider_elem.get('type', '')
            provider_name = provider_elem.find('narrative')
            data['provider_org_name'] = self._get_text_content(provider_name)
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
            data['receiver_org_name'] = self._get_text_content(receiver_name)
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
        data['name'] = self._get_text_content(name_elem)
        data['name_lang'] = name_elem.get(xml_lang, '') if name_elem is not None else ''

        desc_elem = location_elem.find('description/narrative')
        data['description'] = self._get_text_content(desc_elem)
        data['description_lang'] = desc_elem.get(xml_lang, '') if desc_elem is not None else ''

        activity_desc_elem = location_elem.find('activity-description/narrative')
        data['activity_description'] = self._get_text_content(activity_desc_elem)
        data['activity_description_lang'] = activity_desc_elem.get(xml_lang, '') if activity_desc_elem is not None else ''

        # Coordinates
        point_elem = location_elem.find('point/pos')
        if point_elem is not None and point_elem.text:
            coords = self._get_text_content(point_elem).split()
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
        data['title'] = self._get_text_content(title_elem)
        data['title_lang'] = (
            title_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if title_elem is not None else ''
        )

        desc_elem = doc_elem.find('description/narrative')
        data['description'] = self._get_text_content(desc_elem)
        data['description_lang'] = (
            desc_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if desc_elem is not None else ''
        )

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
        data['title'] = self._get_text_content(title_elem)

        desc_elem = result_elem.find('description/narrative')
        data['description'] = self._get_text_content(desc_elem)

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
            if narrative is not None:
                data['title'] = self._get_text_content(narrative).strip()

        # Description
        desc_elem = indicator_elem.find('description')
        if desc_elem is not None:
            narrative = desc_elem.find('narrative')
            if narrative is not None:
                data['description'] = self._get_text_content(narrative).strip()

        # Baseline
        baseline_elem = indicator_elem.find('baseline')
        if baseline_elem is not None:
            data['baseline_year'] = baseline_elem.get('year', '')
            data['baseline_iso_date'] = baseline_elem.get('iso-date', '')
            data['baseline_value'] = baseline_elem.get('value', '')

            comment = baseline_elem.find('comment/narrative')
            if comment is not None:
                data['baseline_comment'] = self._get_text_content(comment).strip()

        return data

    def _extract_contact_data(self, contact_elem: ET.Element, activity_id: str) -> Dict[str, str]:
        """Extract contact information data."""
        data = {'activity_identifier': activity_id}

        data['contact_type'] = contact_elem.get('type', '')

        org_elem = contact_elem.find('organisation/narrative')
        data['organisation'] = self._get_text_content(org_elem)
        data['organisation_lang'] = (
            org_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if org_elem is not None else ''
        )

        dept_elem = contact_elem.find('department/narrative')
        data['department'] = self._get_text_content(dept_elem)
        data['department_lang'] = (
            dept_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if dept_elem is not None else ''
        )

        person_elem = contact_elem.find('person-name/narrative')
        data['person_name'] = self._get_text_content(person_elem)
        data['person_name_lang'] = (
            person_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if person_elem is not None else ''
        )
        data['person_name_present'] = '1' if person_elem is not None else '0'

        job_elem = contact_elem.find('job-title/narrative')
        data['job_title'] = self._get_text_content(job_elem)
        data['job_title_lang'] = (
            job_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if job_elem is not None else ''
        )

        tel_elem = contact_elem.find('telephone')
        data['telephone'] = self._get_text_content(tel_elem)

        email_elem = contact_elem.find('email')
        data['email'] = self._get_text_content(email_elem)
        data['email_present'] = '1' if email_elem is not None else '0'

        website_elem = contact_elem.find('website')
        data['website'] = self._get_text_content(website_elem)

        addr_elem = contact_elem.find('mailing-address/narrative')
        data['mailing_address'] = self._get_text_content(addr_elem)
        data['mailing_address_lang'] = (
            addr_elem.get('{http://www.w3.org/XML/1998/namespace}lang', '') if addr_elem is not None else ''
        )

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
            data['narrative'] = self._get_text_content(narrative)
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
                'contact_info': [],
                'conditions': [],
                'descriptions': [],
                'country_budget_items': []
            }

        # Group related data
        for csv_type in [
            'participating_orgs', 'sectors', 'budgets', 'transactions',
            'transaction_sectors', 'locations', 'documents', 'results', 'indicators', 'indicator_periods',
            'activity_date', 'contact_info', 'conditions', 'descriptions', 'country_budget_items'
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

    def _build_activity_from_data(self, data: Dict[str, Any]) -> Activity:  # noqa: C901
        """Build an Activity object from grouped data."""
        main_data = data['main']

        # Parse humanitarian: "" -> None, "0" -> False, "1" -> True
        humanitarian_value = main_data.get('humanitarian', '')
        if humanitarian_value == '':
            humanitarian = None
        elif humanitarian_value == '0':
            humanitarian = False
        else:  # '1' or any other truthy value
            humanitarian = True

        # Get the activity's default language
        default_lang = main_data.get('xml_lang', 'en')

        # Helper function to create narrative with conditional lang
        def create_narrative(text: str, lang_value: str) -> Narrative:
            """Create Narrative with lang only if it was in the original XML."""
            if lang_value:  # If we have a lang value from CSV (even if empty string was stored)
                return Narrative(text=text, lang=lang_value)
            else:  # No lang in original XML
                return Narrative(text=text)

        # Create basic activity
        activity = Activity(
            iati_identifier=main_data['activity_identifier'],
            reporting_org=OrganizationRef(
                ref=main_data.get('reporting_org_ref', ''),
                type=main_data.get('reporting_org_type') or None,
                narratives=[
                    create_narrative(
                        main_data.get('reporting_org_name', ''),
                        main_data.get('reporting_org_name_lang', '')
                    )
                ] if main_data.get('reporting_org_name') else [],
                secondary_reporter=(
                    True if main_data.get('reporting_org_secondary_reporter') == '1'
                    else False if main_data.get('reporting_org_secondary_reporter') == '0'
                    else None
                )
            ),
            title=[
                create_narrative(
                    main_data.get('title', ''),
                    main_data.get('title_lang', '')
                )
            ] if main_data.get('title') else [],
            description=[],
            activity_status=self._parse_activity_status(main_data.get('activity_status')),
            default_currency=main_data.get('default_currency', 'USD'),
            humanitarian=humanitarian,
            hierarchy=main_data.get('hierarchy') or None,
            last_updated_datetime=main_data.get('last_updated_datetime'),
            xml_lang=default_lang,
            activity_scope=self._parse_activity_scope(main_data.get('activity_scope')),
            conditions_attached=main_data.get('conditions_attached') or None,
            conditions=data.get('conditions', []),
            default_flow_type=main_data.get('default_flow_type') or None,
            default_finance_type=main_data.get('default_finance_type') or None,
            default_aid_type=main_data.get('default_aid_type') or None,
            default_tied_status=main_data.get('default_tied_status') or None
        )

        descriptions = self._build_descriptions_from_rows(data['descriptions'])
        if descriptions:
            activity.description = descriptions
        elif main_data.get('description'):
            activity.description = [{
                "narratives": [
                    create_narrative(
                        main_data.get('description', ''),
                        main_data.get('description_lang', '')
                    )
                ]
            }]

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
            trans_type = trans_data.get('transaction_type')  # NEW: Get transaction type

            # Get unique transaction sectors for THIS specific transaction (ref + type)
            seen_sectors = set()
            transaction_sectors_data = []
            for row in data.get('transaction_sectors', []):
                if (
                    row.get('transaction_ref') == trans_ref and
                    row.get('transaction_type') == trans_type and
                    row.get('activity_identifier') == activity.iati_identifier
                ):
                    sector_key = (row.get('sector_code', ''), row.get('vocabulary', '1'))
                    if sector_key not in seen_sectors:
                        seen_sectors.add(sector_key)
                        transaction_sectors_data.append(row)

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

        # Add conditions_attached attribute
        conditions_attached = main_data.get('conditions_attached', '')
        if conditions_attached != '':
            # Store as custom attribute on activity
            activity.__dict__['conditions_attached'] = conditions_attached

        # Store individual conditions
        if data.get('conditions'):
            activity.__dict__['conditions'] = data['conditions']

        # Add country budget items
        activity.country_budget_items = self._build_country_budget_items(data['country_budget_items'])

        return activity

    def _build_country_budget_items(self, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Build country budget items from CSV rows."""
        if not rows:
            return []

        # Group by vocabulary
        # Although schema allows max 1 country-budget-items element,
        # we group by vocabulary to be safe and support potential multiple elements
        # or just to correctly structure the single element.
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

    def _add_default_types_from_main_data(self, activity: Activity, main_data: Dict[str, str]) -> None:
        """Add collaboration type from main data."""
        # Add collaboration type if present
        collaboration_type = main_data.get('collaboration_type')
        if collaboration_type:
            try:
                activity.collaboration_type = CollaborationType(collaboration_type)
            except (ValueError, TypeError):
                pass  # Skip invalid collaboration type

    def _build_participating_org(self, org_data: Dict[str, str]) -> ParticipatingOrg:
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

    def _build_sector(self, sector_data: Dict[str, str]) -> Dict[str, Any]:
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

    def _build_budget(self, budget_data: Dict[str, str]) -> Budget:
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

    def _build_transaction(  # noqa C901
        self,
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
            transaction_args['aid_type'] = {"code": trans_data['aid_type']}
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

    def _build_location(self, location_data: Dict[str, str]) -> Location:
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

    def _build_document(self, doc_data: Dict[str, str]) -> DocumentLink:
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

    def _build_contact_info(self, contact_data: Dict[str, str]) -> ContactInfo:
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

    def _build_descriptions_from_rows(
        self, rows: List[Dict[str, str]]
    ) -> List[Dict[str, List[Narrative]]]:
        """Reconstruct description structures from CSV rows."""
        if not rows:
            return []

        grouped: Dict[str, Dict[str, Any]] = {}
        for row in sorted(
            rows,
            key=lambda r: (
                self._safe_int(r.get('description_sequence')),
                self._safe_int(r.get('narrative_sequence'))
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
        for seq in sorted(grouped.keys(), key=self._safe_int):
            entry = grouped[seq]
            desc_dict: Dict[str, Any] = {
                "narratives": entry['narratives'] or [Narrative(text='')]
            }
            if entry['type']:
                desc_dict["type"] = entry['type']
            descriptions.append(desc_dict)

        return descriptions

    def _safe_int(self, value: Optional[str], default: int = 0) -> int:
        """Safely convert string values to integers for ordering."""
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default

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
                'recipient_country_lang': 'es',
                'recipient_region_code': '',
                'recipient_region_name': '',
                'recipient_region_lang': '',
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
                    'org_name_lang': 'en',
                    'org_type': '40',
                    'role': '1'  # Funding
                },
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'org_ref': 'CR-MOPT',
                    'org_name': 'Ministry of Public Works and Transportation, Costa Rica',
                    'org_name_lang': 'es',
                    'org_type': '10',
                    'role': '4'  # Implementing
                }
            ]
        elif csv_type == 'contact_info':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'contact_type': '1',
                'organisation': 'Central American Bank for Economic Integration',
                'organisation_lang': 'en',
                'department': 'Infrastructure Projects Division',
                'department_lang': 'en',
                'person_name': 'Ana García',
                'person_name_lang': 'es',
                'person_name_present': '1',
                'job_title': 'Project Manager',
                'job_title_lang': 'en',
                'telephone': '+506-2123-4567',
                'email': 'ana.garcia@bcie.org',
                'email_present': '1',
                'website': 'https://www.bcie.org',
                'mailing_address': 'Tegucigalpa M.D.C., Honduras',
                'mailing_address_lang': 'es'
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
        elif csv_type == 'descriptions':
            return [
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'description_type': '1',
                    'description_sequence': '1',
                    'narrative': 'Primary activity description',
                    'narrative_lang': 'en',
                    'narrative_sequence': '1'
                },
                {
                    'activity_identifier': 'XM-DAC-46002-CR-2025',
                    'description_type': '2',
                    'description_sequence': '2',
                    'narrative': 'Secondary summary for beneficiaries',
                    'narrative_lang': 'en',
                    'narrative_sequence': '1'
                }
            ]
        elif csv_type == 'documents':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'url': 'https://example.org/documents/project-summary.pdf',
                'format': 'application/pdf',
                'title': 'Project summary',
                'title_lang': 'en',
                'description': 'Detailed design and financing summary',
                'description_lang': 'en',
                'category_code': 'A01',
                'language_code': 'en',
                'document_date': '2024-03-15'
            }]
        elif csv_type == 'country_budget_items':
            return [{
                'activity_identifier': 'XM-DAC-46002-CR-2025',
                'vocabulary': '1',
                'budget_item_code': 'CR-2025-01',
                'budget_item_percentage': '50',
                'description': 'Road rehabilitation',
                'description_lang': 'en'
            }]
        # ...existing code for other examples...

        return []

    def _create_summary_file(
        self, csv_folder: Path, data_collections: Dict[str, List[Dict]], root_attributes: Dict[str, str] = None
    ) -> None:
        """Create a summary file with statistics and root attributes."""
        summary_path = csv_folder / 'summary.txt'

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("IATI CSV Conversion Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Conversion completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Write root-level attributes if provided
            if root_attributes:
                f.write("Root Attributes:\n")
                for key, value in root_attributes.items():
                    if value:  # Only write non-empty values
                        f.write(f"  {key}: {value}\n")
                f.write("\n")

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
