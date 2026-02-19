"""
IATI Organisation XML Generator Base Module.

Main converter class for organisations with multi-CSV support.
"""

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from .process_xml.extractors import (
    extract_organisation_basic_info,
    extract_organisation_names,
    extract_organisation_budgets,
    extract_organisation_expenditures,
    extract_organisation_documents
)
from .process_csv.builders import (
    build_organisation_budget,
    build_organisation_expenditure,
    build_organisation_document
)

logger = logging.getLogger(__name__)


def _set_attribute(element: ET.Element, name: str, value: Any) -> None:
    """Set XML attribute if value is not None or empty."""
    if value is not None and str(value).strip():
        element.set(name, str(value).strip())


def _add_narrative(parent: ET.Element, text: str, lang: Optional[str] = None) -> None:
    """Add a narrative element with optional language attribute."""
    if not text or not str(text).strip():
        return

    narr = ET.SubElement(parent, "narrative")
    narr.text = str(text).strip()

    if lang and str(lang).strip():
        narr.set("xml:lang", str(lang).strip())


def _get_field(row: Dict[str, Any], field_names: List[str], default: str = "") -> str:
    """Get field value from row by trying multiple possible field names."""
    row_lower = {k.lower().strip(): v for k, v in row.items()}

    for name in field_names:
        key = name.lower().strip()
        if key in row_lower:
            value = row_lower[key]
            if value is None:
                return default

            if PANDAS_AVAILABLE and pd.isna(value):
                return default

            value_str = str(value).strip()
            if value_str:
                return value_str

    return default


def _pretty_xml(element: ET.Element) -> str:
    """Convert an XML Element to a pretty-printed string."""
    rough_string = ET.tostring(element, "utf-8")
    return minidom.parseString(rough_string).toprettyxml(indent="  ")


@dataclass
class OrganisationBudget:
    """Budget information for an IATI organisation."""
    kind: str
    status: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    value: Optional[str] = None
    currency: Optional[str] = None
    value_date: Optional[str] = None
    recipient_org_ref: Optional[str] = None
    recipient_org_type: Optional[str] = None
    recipient_org_name: Optional[str] = None
    recipient_country_code: Optional[str] = None
    recipient_region_code: Optional[str] = None
    recipient_region_vocabulary: Optional[str] = None
    budget_lines: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        """Validate budget kind."""
        valid_kinds = [
            'total-budget',
            'recipient-org-budget',
            'recipient-country-budget',
            'recipient-region-budget'
        ]
        if self.kind not in valid_kinds:
            raise ValueError(f"Invalid budget kind: {self.kind}")


@dataclass
class OrganisationExpenditure:
    """Expenditure information for an IATI organisation."""
    period_start: str
    period_end: str
    value: str
    currency: Optional[str] = None
    value_date: Optional[str] = None
    expense_lines: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class OrganisationDocument:
    """Document link information for an IATI organisation."""
    url: str
    format: str = "text/html"
    title: Optional[str] = None
    category_code: Optional[str] = None
    language: Optional[str] = None
    document_date: Optional[str] = None


@dataclass
class OrganisationRecord:
    """IATI Organisation record containing all organisation information."""
    org_identifier: str
    name: str
    names: Dict[str, str] = field(default_factory=dict)
    reporting_org_ref: Optional[str] = None
    reporting_org_type: Optional[str] = None
    reporting_org_name: Optional[str] = None
    reporting_org_lang: Optional[str] = None
    xml_lang: Optional[str] = None
    default_currency: Optional[str] = None
    budgets: List[OrganisationBudget] = field(default_factory=list)
    expenditures: List[OrganisationExpenditure] = field(default_factory=list)
    documents: List[OrganisationDocument] = field(default_factory=list)

    def __post_init__(self):
        """Validate required fields."""
        if not self.org_identifier:
            raise ValueError("Missing required field: org_identifier")
        if not self.name:
            raise ValueError("Missing required field: name")

        if not self.names:
            self.names = {"": self.name}
        elif "" not in self.names and (not self.xml_lang or self.xml_lang not in self.names):
            self.names[""] = self.name


class IatiOrganisationXMLGenerator:
    """Generator for IATI organisation XML files."""

    def __init__(self, iati_version: str = "2.03"):
        """Initialize the XML generator."""
        self.iati_version = iati_version

    def build_root_element(self) -> ET.Element:
        """Create the root iati-organisations element."""
        root = ET.Element("iati-organisations")
        _set_attribute(root, "version", self.iati_version)
        _set_attribute(
            root, "generated-datetime",
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        _set_attribute(root, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        _set_attribute(
            root, "xmlns:xsi",
            "http://www.w3.org/2001/XMLSchema-instance"
        )
        return root

    def add_organisation(self, root: ET.Element, record: OrganisationRecord) -> ET.Element:
        """Add an organisation to the XML root element."""
        org_el = ET.SubElement(root, "iati-organisation")
        _set_attribute(
            org_el, "last-updated-datetime",
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        _set_attribute(org_el, "xml:lang", record.xml_lang or "en")

        if record.default_currency:
            _set_attribute(org_el, "default-currency", record.default_currency)

        oid = ET.SubElement(org_el, "organisation-identifier")
        oid.text = record.org_identifier

        name_el = ET.SubElement(org_el, "name")
        if record.names:
            for lang_code, name_text in record.names.items():
                _add_narrative(name_el, name_text, lang_code if lang_code else None)
        else:
            _add_narrative(name_el, record.name)

        if record.reporting_org_ref or record.reporting_org_type or record.reporting_org_name:
            rep_org = ET.SubElement(org_el, "reporting-org")
            _set_attribute(rep_org, "ref", record.reporting_org_ref)
            _set_attribute(rep_org, "type", record.reporting_org_type)
            _add_narrative(rep_org, record.reporting_org_name, record.reporting_org_lang)

        for budget in record.budgets:
            self._add_budget(org_el, budget)

        for expenditure in record.expenditures:
            self._add_expenditure(org_el, expenditure)

        for document in record.documents:
            self._add_document_link(org_el, document)

        return org_el

    def _add_budget(self, org_el: ET.Element, budget: OrganisationBudget) -> None:
        """Add a budget element to the organisation."""
        budget_el = ET.SubElement(org_el, budget.kind)
        _set_attribute(budget_el, "status", budget.status)

        if budget.kind == "recipient-org-budget" and budget.recipient_org_ref:
            recip_org = ET.SubElement(budget_el, "recipient-org")
            _set_attribute(recip_org, "ref", budget.recipient_org_ref)
            _set_attribute(recip_org, "type", budget.recipient_org_type)
            _add_narrative(recip_org, budget.recipient_org_name)

        elif budget.kind == "recipient-country-budget" and budget.recipient_country_code:
            recip_country = ET.SubElement(budget_el, "recipient-country")
            _set_attribute(recip_country, "code", budget.recipient_country_code)

        elif budget.kind == "recipient-region-budget" and budget.recipient_region_code:
            recip_region = ET.SubElement(budget_el, "recipient-region")
            _set_attribute(recip_region, "code", budget.recipient_region_code)
            _set_attribute(recip_region, "vocabulary", budget.recipient_region_vocabulary or "1")

        if budget.period_start:
            period_start = ET.SubElement(budget_el, "period-start")
            _set_attribute(period_start, "iso-date", budget.period_start)

        if budget.period_end:
            period_end = ET.SubElement(budget_el, "period-end")
            _set_attribute(period_end, "iso-date", budget.period_end)

        if budget.value:
            value_el = ET.SubElement(budget_el, "value")
            value_el.text = str(budget.value)
            _set_attribute(value_el, "currency", budget.currency)
            _set_attribute(value_el, "value-date", budget.value_date or budget.period_start)

        for line in budget.budget_lines:
            if "value" in line:
                pass

    def _add_expenditure(self, org_el: ET.Element, expenditure: OrganisationExpenditure) -> None:
        """Add a total-expenditure element to the organisation."""
        exp_el = ET.SubElement(org_el, "total-expenditure")

        period_start = ET.SubElement(exp_el, "period-start")
        _set_attribute(period_start, "iso-date", expenditure.period_start)

        period_end = ET.SubElement(exp_el, "period-end")
        _set_attribute(period_end, "iso-date", expenditure.period_end)

        value_el = ET.SubElement(exp_el, "value")
        value_el.text = str(expenditure.value)
        _set_attribute(value_el, "currency", expenditure.currency)
        _set_attribute(value_el, "value-date", expenditure.value_date or expenditure.period_start)

        for line in expenditure.expense_lines:
            if "value" in line:
                pass

    def _add_document_link(self, org_el: ET.Element, document: OrganisationDocument) -> None:
        """Add a document-link element to the organisation."""
        doc_el = ET.SubElement(org_el, "document-link")
        _set_attribute(doc_el, "url", document.url)
        _set_attribute(doc_el, "format", document.format)

        if document.title:
            title_el = ET.SubElement(doc_el, "title")
            _add_narrative(title_el, document.title)

        if document.category_code:
            category = ET.SubElement(doc_el, "category")
            _set_attribute(category, "code", document.category_code)

        if document.language:
            language = ET.SubElement(doc_el, "language")
            _set_attribute(language, "code", document.language)

        if document.document_date:
            doc_date = ET.SubElement(doc_el, "document-date")
            _set_attribute(doc_date, "iso-date", document.document_date)

    def to_string(self, root: ET.Element) -> str:
        """Convert the XML to a properly formatted string."""
        xml_string = _pretty_xml(root)

        repo_url = "https://github.com/okfn/okfn-iati"
        comment = f"<!-- Generated by OKFN-IATI Organisation XML Generator: {repo_url} -->"

        xml_declaration_end = xml_string.find("?>") + 2
        xml_string = xml_string[:xml_declaration_end] + "\n" + comment + xml_string[xml_declaration_end:]

        return xml_string

    def save_to_file(self, root: ET.Element, file_path: Union[str, Path]) -> None:
        """Save the XML to a file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_string(root))


class IatiOrganisationMultiCsvConverter:
    """Multi-CSV converter for IATI organisation data."""

    csv_files = {
        'organisations': {
            'filename': 'organisations.csv',
            "required": True,
            'columns': [
                'organisation_identifier', 'name', 'reporting_org_ref',
                'reporting_org_type', 'reporting_org_name', 'reporting_org_lang',
                'default_currency', 'xml_lang'
            ]
        },
        'names': {
            'filename': 'names.csv',
            "required": False,
            'columns': ['organisation_identifier', 'language', 'name']
        },
        'budgets': {
            'filename': 'budgets.csv',
            "required": False,
            'columns': [
                'organisation_identifier', 'budget_kind', 'budget_status',
                'period_start', 'period_end', 'value', 'currency', 'value_date',
                'recipient_org_ref', 'recipient_org_type', 'recipient_org_name',
                'recipient_country_code', 'recipient_region_code', 'recipient_region_vocabulary'
            ]
        },
        'expenditures': {
            'filename': 'expenditures.csv',
            "required": False,
            'columns': [
                'organisation_identifier', 'period_start', 'period_end',
                'value', 'currency', 'value_date'
            ]
        },
        'documents': {
            'filename': 'documents.csv',
            "required": False,
            'columns': [
                'organisation_identifier', 'url', 'format', 'title',
                'category_code', 'language', 'document_date'
            ]
        }
    }

    def __init__(self):
        """Initialize the multi-CSV converter."""
        self.latest_errors: List[str] = []
        self.latest_warnings: List[str] = []
        self.xml_generator = IatiOrganisationXMLGenerator()

    @classmethod
    def required_csv_files(cls) -> list[str]:
        return [
            cfg["filename"]
            for cfg in cls.csv_files.values()
            if cfg.get("required")
        ]

    @classmethod
    def expected_csv_files(cls) -> list[str]:
        return [cfg["filename"] for cfg in cls.csv_files.values()]

    def xml_to_csv_folder(
        self,
        xml_input: Union[str, Path],
        output_folder: Union[str, Path]
    ) -> bool:
        """Convert IATI organisation XML to multiple CSV files in a folder."""
        self.latest_errors = []
        self.latest_warnings = []
        try:
            xml_path = Path(xml_input)
            if not xml_path.exists():
                raise ValueError(f"XML file not found: {xml_path}")

            tree = ET.parse(xml_path)
            root = tree.getroot()

            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)

            organisations_data = []
            names_data = []
            budgets_data = []
            expenditures_data = []
            documents_data = []

            for org_elem in root.findall('.//iati-organisation'):
                basic_info = extract_organisation_basic_info(org_elem)
                org_id = basic_info['organisation_identifier']

                organisations_data.append(basic_info)
                names_data.extend(extract_organisation_names(org_elem, org_id))
                budgets_data.extend(extract_organisation_budgets(org_elem, org_id))
                expenditures_data.extend(extract_organisation_expenditures(org_elem, org_id))
                documents_data.extend(extract_organisation_documents(org_elem, org_id))

            self._write_organisations_csv(organisations_data, output_path / "organisations.csv")

            multi_name_count = 0
            for org_id in {n["organisation_identifier"] for n in names_data}:
                if sum(1 for n in names_data if n["organisation_identifier"] == org_id) > 1:
                    multi_name_count += 1

            if multi_name_count > 0:
                self._write_names_csv(names_data, output_path / "names.csv")

            if budgets_data:
                self._write_budgets_csv(budgets_data, output_path / "budgets.csv")

            if expenditures_data:
                self._write_expenditures_csv(expenditures_data, output_path / "expenditures.csv")

            if documents_data:
                self._write_documents_csv(documents_data, output_path / "documents.csv")

            logger.info(f"Successfully converted organisation XML to CSV folder: {output_path}")
            return True

        except Exception as e:
            error_msg = f"Error during XML to CSV conversion: {str(e)}"
            self.latest_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def csv_folder_to_xml(
        self,
        input_folder: Union[str, Path],
        xml_output: Union[str, Path]
    ) -> bool:
        """Convert multiple CSV files to IATI organisation XML."""
        self.latest_errors = []
        self.latest_warnings = []
        try:
            folder_path = Path(input_folder)
            if not folder_path.exists():
                raise ValueError(f"CSV folder not found: {folder_path}")

            organisations = self._read_organisations_csv(folder_path / "organisations.csv")
            names = self._read_names_csv(folder_path / "names.csv") if (folder_path / "names.csv").exists() else []
            budgets = self._read_budgets_csv(folder_path / "budgets.csv") if (folder_path / "budgets.csv").exists() else []
            expenditures = self._read_expenditures_csv(
                folder_path / "expenditures.csv"
            ) if (folder_path / "expenditures.csv").exists() else []
            documents = self._read_documents_csv(
                folder_path / "documents.csv"
            ) if (folder_path / "documents.csv").exists() else []

            org_data_map = {}
            for org in organisations:
                org_id = org['organisation_identifier']
                org_data_map[org_id] = {
                    'basic_info': org,
                    'names': [],
                    'budgets': [],
                    'expenditures': [],
                    'documents': []
                }

            for name in names:
                org_id = name['organisation_identifier']
                if org_id in org_data_map:
                    org_data_map[org_id]['names'].append(name)

            for budget in budgets:
                org_id = budget['organisation_identifier']
                if org_id in org_data_map:
                    org_data_map[org_id]['budgets'].append(budget)

            for expenditure in expenditures:
                org_id = expenditure['organisation_identifier']
                if org_id in org_data_map:
                    org_data_map[org_id]['expenditures'].append(expenditure)

            for document in documents:
                org_id = document['organisation_identifier']
                if org_id in org_data_map:
                    org_data_map[org_id]['documents'].append(document)

            records = []
            for org_id, data in org_data_map.items():
                record = self._create_organisation_record_from_csv_data(data)
                records.append(record)

            root = self.xml_generator.build_root_element()
            for record in records:
                self.xml_generator.add_organisation(root, record)

            output_path = Path(xml_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.xml_generator.save_to_file(root, output_path)

            logger.info(f"Successfully converted CSV folder to organisation XML: {output_path}")
            return True

        except Exception as e:
            error_msg = f"Failed to convert CSV folder to XML: {str(e)}"
            self.latest_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def _write_organisations_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write organisations data to CSV."""
        columns = [
            'organisation_identifier', 'name', 'reporting_org_ref',
            'reporting_org_type', 'reporting_org_name', 'reporting_org_lang',
            'default_currency', 'xml_lang'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

    def _write_names_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write names data to CSV."""
        columns = ['organisation_identifier', 'language', 'name']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

    def _write_budgets_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write budgets data to CSV."""
        columns = [
            'organisation_identifier', 'budget_kind', 'budget_status',
            'period_start', 'period_end', 'value', 'currency', 'value_date',
            'recipient_org_ref', 'recipient_org_type', 'recipient_org_name',
            'recipient_country_code', 'recipient_region_code', 'recipient_region_vocabulary'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

    def _write_expenditures_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write expenditures data to CSV."""
        columns = [
            'organisation_identifier', 'period_start', 'period_end',
            'value', 'currency', 'value_date'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

    def _write_documents_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write documents data to CSV."""
        columns = [
            'organisation_identifier', 'url', 'format', 'title',
            'category_code', 'language', 'document_date'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

    def _read_organisations_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read organisations CSV file."""
        organisations = []

        if not csv_path.exists():
            return organisations

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            organisations = list(reader)

        return organisations

    def _read_names_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read names CSV file."""
        names = []

        if not csv_path.exists():
            return names

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            names = list(reader)

        return names

    def _read_budgets_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read budgets CSV file."""
        budgets = []

        if not csv_path.exists():
            return budgets

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            budgets = list(reader)

        return budgets

    def _read_expenditures_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read expenditures CSV file."""
        expenditures = []

        if not csv_path.exists():
            return expenditures

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expenditures = list(reader)

        return expenditures

    def _read_documents_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read documents CSV file."""
        documents = []

        if not csv_path.exists():
            return documents

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)

        return documents

    def _create_organisation_record_from_csv_data(self, data: Dict[str, Any]) -> OrganisationRecord:
        """Create OrganisationRecord from CSV data."""
        basic_info = data['basic_info']

        names_dict = {}
        for name_data in data['names']:
            lang = name_data.get('language', '')
            names_dict[lang] = name_data.get('name', '')

        record = OrganisationRecord(
            org_identifier=basic_info['organisation_identifier'],
            name=basic_info['name'],
            names=names_dict,
            reporting_org_ref=basic_info.get('reporting_org_ref', ''),
            reporting_org_type=basic_info.get('reporting_org_type', ''),
            reporting_org_name=basic_info.get('reporting_org_name', ''),
            reporting_org_lang=basic_info.get('reporting_org_lang', ''),
            xml_lang=basic_info.get('xml_lang', 'en'),
            default_currency=basic_info.get('default_currency', 'USD')
        )

        for budget_data in data['budgets']:
            budget_dict = build_organisation_budget(budget_data)
            budget = OrganisationBudget(**budget_dict)
            record.budgets.append(budget)

        for exp_data in data['expenditures']:
            exp_dict = build_organisation_expenditure(exp_data)
            expenditure = OrganisationExpenditure(**exp_dict)
            record.expenditures.append(expenditure)

        for doc_data in data['documents']:
            doc_dict = build_organisation_document(doc_data)
            document = OrganisationDocument(**doc_dict)
            record.documents.append(document)

        return record
