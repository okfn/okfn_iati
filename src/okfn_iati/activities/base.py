"""
IATI Multi-CSV Converter Base Class.

This module provides the main converter class for IATI data.
"""

import csv
import shutil
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
from datetime import datetime

from okfn_iati.models import Activity, Narrative, OrganizationRef, IatiActivities
from okfn_iati.xml_generator import IatiXmlGenerator

# Import extractors
from .process_xml.extractors import (
    get_activity_identifier, extract_description_data,
    extract_indicator_period_data, extract_transaction_sector_data,
    extract_country_budget_items, extract_main_activity_data,
    extract_condition_data, extract_participating_org_data,
    extract_sector_data, extract_budget_data, extract_transaction_data,
    extract_location_data, extract_document_data, extract_result_data,
    extract_indicator_data, extract_contact_data, extract_activity_date_data
)

# Import builders
from .process_csv.builders import (
    build_participating_org, build_sector, build_budget, build_transaction,
    build_location, build_document, build_contact_info,
    build_result_with_indicators, build_country_budget_items,
    build_descriptions_from_rows, parse_activity_status,
    parse_activity_scope, add_dates_from_main_data, add_geography_from_main_data,
    add_default_types_from_main_data, build_activity_date
)


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

    csv_files = {
            'activities': {
                'filename': 'activities.csv',
                'required': True,
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
                    'reporting_org_role',
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
                    'default_aid_type_vocabulary',
                    'default_tied_status',
                    'conditions_attached'
                ]
            },
            'participating_orgs': {
                'filename': 'participating_orgs.csv',
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                    'aid_type_vocabulary',
                    'tied_status',
                    'humanitarian',
                    'recipient_region'
                ]
            },
            'transaction_sectors': {
                'filename': 'transaction_sectors.csv',
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
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
                'required': False,
                'columns': [
                    'activity_identifier',  # Foreign key to activities
                    'condition_type',
                    'condition_text'
                ]
            },
            'descriptions': {
                'filename': 'descriptions.csv',
                'required': False,
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
                'required': False,
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

    def __init__(self):
        self.xml_generator = IatiXmlGenerator()
        # Storage latest errors and warnings in case an action failed
        self.latest_errors: List[str] = []
        self.latest_warnings: List[str] = []

    @classmethod
    def required_csv_files(cls) -> list[str]:
        return [cfg["filename"] for cfg in cls.csv_files.values() if cfg.get("required")]

    @classmethod
    def expected_csv_files(cls) -> list[str]:
        return [cfg["filename"] for cfg in cls.csv_files.values()]

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
        self.latest_errors = []
        self.latest_warnings = []
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
            self.latest_errors.append(str(e))
            print(f"❌ Error converting XML to CSV: {e}")
            return False

    def csv_folder_to_xml(
        self,
        csv_folder: Union[str, Path],
        xml_output: Union[str, Path],
        validate_output: bool = True,
        validate_csv: bool = False
    ) -> bool:
        """
        Convert multiple CSV files in a folder to IATI XML.

        Args:
            csv_folder: Path to folder containing CSV files
            xml_output: Path to output XML file
            validate_output: If True, validate the generated XML
            validate_csv: If True, run CSV-level validation before conversion.
                When validation finds errors, conversion is aborted and
                the error details are stored in self.latest_errors.

        Returns:
            True if conversion was successful
        """
        self.latest_errors = []
        self.latest_warnings = []

        csv_folder = Path(csv_folder)

        if not csv_folder.exists():
            error_msg = f"❌ Error: CSV folder does not exist: {csv_folder}"
            print(error_msg)
            self.latest_errors.append(error_msg)
            return False

        if validate_csv:
            from ..csv_validators import CsvFolderValidator
            csv_result = CsvFolderValidator().validate_folder(csv_folder)
            if not csv_result.is_valid:
                for issue in csv_result.errors:
                    self.latest_errors.append(str(issue))
                for issue in csv_result.warnings:
                    self.latest_warnings.append(str(issue))
                return False
            for issue in csv_result.warnings:
                self.latest_warnings.append(str(issue))

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
                from ..iati_schema_validator import IatiValidator
                validator = IatiValidator()
                xml_string = self.xml_generator.generate_iati_activities_xml(iati_activities)
                is_valid, errors = validator.validate(xml_string)

                if not is_valid:
                    # errors is a dict like {'schema_errors': schema_errors, 'ruleset_errors': ruleset_errors}
                    # Each is a list of error strings
                    schema_errors = errors.get('schema_errors', [])
                    ruleset_errors = errors.get('ruleset_errors', [])
                    # Tag them and create a single list
                    all_errors = [f"Schema: {err}" for err in schema_errors] + [f"Ruleset: {err}" for err in ruleset_errors]
                    self.latest_errors = all_errors
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

    def _extract_activity_to_collections(  # noqa: C901
        self,
        activity_elem: ET.Element,
        data_collections: Dict[str, List[Dict]]
    ) -> None:
        """Extract activity data into separate collections."""
        activity_id = get_activity_identifier(activity_elem)

        # Extract main activity data
        activity_data = extract_main_activity_data(activity_elem, activity_id, self.csv_files)
        data_collections['activities'].append(activity_data)

        # Extract descriptions
        description_index = 0
        for desc_elem in activity_elem.findall('description'):
            description_index += 1
            narratives = desc_elem.findall('narrative') or [None]
            for narrative_index, narrative_elem in enumerate(narratives, start=1):
                description_row = extract_description_data(
                    desc_elem,
                    activity_id,
                    description_index,
                    narrative_elem,
                    narrative_index
                )
                data_collections['descriptions'].append(description_row)

        # Extract participating organizations
        for org_elem in activity_elem.findall('participating-org'):
            org_data = extract_participating_org_data(org_elem, activity_id)
            data_collections['participating_orgs'].append(org_data)

        # Extract sectors
        for sector_elem in activity_elem.findall('sector'):
            sector_data = extract_sector_data(sector_elem, activity_id)
            data_collections['sectors'].append(sector_data)

        # Extract budgets
        for budget_elem in activity_elem.findall('budget'):
            budget_data = extract_budget_data(budget_elem, activity_id)
            data_collections['budgets'].append(budget_data)

        # Extract transactions with deduplication
        seen_transaction_sectors = set()  # Track (activity_id, transaction_ref, transaction_type, sector_code, vocabulary)

        for trans_elem in activity_elem.findall('transaction'):
            trans_data = extract_transaction_data(trans_elem, activity_id)
            data_collections['transactions'].append(trans_data)

            # Extract transaction sectors with deduplication
            transaction_ref = trans_data.get('transaction_ref', '')
            transaction_type = trans_data.get('transaction_type', '')  # NEW: Get transaction type

            for sector_elem in trans_elem.findall('sector'):
                sector_data = extract_transaction_sector_data(
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
            location_data = extract_location_data(location_elem, activity_id)
            data_collections['locations'].append(location_data)

        # Extract documents
        for doc_elem in activity_elem.findall('document-link'):
            doc_data = extract_document_data(doc_elem, activity_id)
            data_collections['documents'].append(doc_data)

        # Extract results and indicators
        result_index = 0
        for result_elem in activity_elem.findall('result'):
            result_index += 1
            result_data = extract_result_data(
                result_elem,
                activity_id,
                result_index
            )
            data_collections['results'].append(result_data)

            # Extract indicators for this result
            indicator_index = 0
            for indicator_elem in result_elem.findall('indicator'):
                indicator_index += 1
                indicator_data = extract_indicator_data(
                    indicator_elem,
                    activity_id,
                    result_data['result_ref'],
                    indicator_index
                )
                data_collections['indicators'].append(indicator_data)

                # Extract periods for this indicator
                indicator_ref = indicator_data.get('indicator_ref', '')
                for period_elem in indicator_elem.findall('period'):
                    period_data = extract_indicator_period_data(
                        period_elem,
                        activity_id,
                        result_data.get('result_ref', ''),
                        indicator_ref
                    )
                    data_collections['indicator_periods'].append(period_data)

        # Extract activity dates
        for date_elem in activity_elem.findall('activity-date'):
            date_data = extract_activity_date_data(date_elem, activity_id)
            data_collections['activity_date'].append(date_data)

        # Extract contact info
        contact_elem = activity_elem.find('contact-info')
        if contact_elem is not None:
            contact_data = extract_contact_data(contact_elem, activity_id)
            data_collections['contact_info'].append(contact_data)

        # Extract conditions
        conditions_elem = activity_elem.find('conditions')
        if conditions_elem is not None:
            for condition_elem in conditions_elem.findall('condition'):
                condition_data = extract_condition_data(condition_elem, activity_id)
                data_collections['conditions'].append(condition_data)

        # Extract country budget items
        for cbi_elem in activity_elem.findall('country-budget-items'):
            data_collections['country_budget_items'].extend(
                extract_country_budget_items(cbi_elem, activity_id)
            )

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
            # Default is the reporting org is the one implementing the activity (role code "4": IMPLEMENTING)
            reporting_org_role=main_data.get('reporting_org_role') or "4",
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
            activity_status=parse_activity_status(main_data.get('activity_status')),
            default_currency=main_data.get('default_currency', 'USD'),
            humanitarian=humanitarian,
            hierarchy=main_data.get('hierarchy') or None,
            last_updated_datetime=main_data.get('last_updated_datetime'),
            xml_lang=default_lang,
            activity_scope=parse_activity_scope(main_data.get('activity_scope')),
            conditions_attached=main_data.get('conditions_attached') or None,
            conditions=data.get('conditions', []),
            default_flow_type=main_data.get('default_flow_type') or None,
            default_finance_type=main_data.get('default_finance_type') or None,
            default_aid_type=main_data.get('default_aid_type') or None,
            default_aid_type_vocabulary=main_data.get('default_aid_type_vocabulary') or None,
            default_tied_status=main_data.get('default_tied_status') or None
        )

        descriptions = build_descriptions_from_rows(data['descriptions'])
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
        add_dates_from_main_data(activity, main_data)

        # Add geographic information
        add_geography_from_main_data(activity, main_data)

        # Add default types from main data
        add_default_types_from_main_data(activity, main_data)

        # Add participating organizations
        for org_data in data['participating_orgs']:
            activity.participating_orgs.append(build_participating_org(org_data))

        # Add sectors
        for sector_data in data['sectors']:
            activity.sectors.append(build_sector(sector_data))

        # Add budgets
        for budget_data in data['budgets']:
            activity.budgets.append(build_budget(budget_data))

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

            activity.transactions.append(build_transaction(trans_data, transaction_sectors_data))

        # Add locations
        for location_data in data['locations']:
            activity.locations.append(build_location(location_data))

        # Add documents
        for doc_data in data['documents']:
            activity.document_links.append(build_document(doc_data))

        # Add activity_dates
        for date_data in data['activity_date']:
            activity.activity_dates.append(build_activity_date(date_data))

        # Add contact info
        for contact_data in data['contact_info']:
            activity.contact_info = build_contact_info(contact_data)
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
            result = build_result_with_indicators(
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
        activity.country_budget_items = build_country_budget_items(data['country_budget_items'])

        return activity

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
                'reporting_org_role': '1',
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
