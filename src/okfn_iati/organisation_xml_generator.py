"""
IATI Organisation XML Generator - Creates IATI-compliant organisation XML files.

This module generates IATI organisation XML files according to the IATI standard v2.03.
Organisation files contain information about the publishing organization and its budgets,
expenditure, and documents - distinct from activity files which describe projects.

References:
- https://iatistandard.org/en/guidance/standard-overview/organisation-infromation/
- https://iatistandard.org/en/iati-standard/203/organisation-standard/
- https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/

"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import csv
import logging

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


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
    # Create a case-insensitive map of the row
    row_lower = {k.lower().strip(): v for k, v in row.items()}

    # Try each possible field name
    for name in field_names:
        key = name.lower().strip()
        if key in row_lower:
            value = row_lower[key]
            # Handle None, empty string, and pandas NA
            if value is None:
                continue

            if PANDAS_AVAILABLE and pd.isna(value):
                continue

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
    """
    Budget information for an IATI organisation.

    Args:
        kind: Type of budget ('total-budget', 'recipient-org-budget',
              'recipient-country-budget', 'recipient-region-budget')
        status: Status of budget (1=Indicative, 2=Committed)
        period_start: Start date of budget period (YYYY-MM-DD)
        period_end: End date of budget period (YYYY-MM-DD)
        value: Budget amount
        currency: Currency code (ISO 4217)
        value_date: Date for currency exchange rate (YYYY-MM-DD)

    Recipient-specific fields:
        recipient_org_ref: Recipient organisation identifier
        recipient_org_type: Recipient organisation type code
        recipient_org_name: Recipient organisation name
        recipient_country_code: Recipient country code
        recipient_region_code: Recipient region code
        recipient_region_vocabulary: Recipient region vocabulary code
    """
    kind: str  # total-budget, recipient-org-budget, recipient-country-budget, recipient-region-budget
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
            raise ValueError(
                f"Invalid budget kind: {self.kind}. Must be one of: {', '.join(valid_kinds)}"
            )


@dataclass
class OrganisationExpenditure:
    """
    Expenditure information for an IATI organisation.

    Args:
        period_start: Start date of expenditure period (YYYY-MM-DD)
        period_end: End date of expenditure period (YYYY-MM-DD)
        value: Expenditure amount
        currency: Currency code (ISO 4217)
        value_date: Date for currency exchange rate (YYYY-MM-DD)
    """
    period_start: str
    period_end: str
    value: str
    currency: Optional[str] = None
    value_date: Optional[str] = None
    expense_lines: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class OrganisationDocument:
    """
    Document link information for an IATI organisation.

    Args:
        url: URL of the document
        format: MIME type format (e.g., 'application/pdf')
        title: Document title
        category_code: Document category code
        language: Document language code
        document_date: Document publication date (YYYY-MM-DD)
    """
    url: str
    format: str = "text/html"
    title: Optional[str] = None
    # https://iatistandard.org/en/iati-standard/203/codelists/documentcategory/
    category_code: Optional[str] = None
    language: Optional[str] = None
    document_date: Optional[str] = None


@dataclass
class OrganisationRecord:
    """
    IATI Organisation record containing all organisation information.

    Args:
        org_identifier: Organisation identifier
        name: Organisation name (primary/default)
        names: Dictionary of names by language code (includes primary name)
        reporting_org_ref: Reporting organisation reference
        reporting_org_type: Reporting organisation type
        reporting_org_name: Reporting organisation name
        reporting_org_lang: Language of reporting org narrative
        xml_lang: Default language for the organisation
        default_currency: Default currency for the organisation
        budgets: List of organisation budgets
        expenditures: List of organisation expenditures
        documents: List of organisation document links
    """
    org_identifier: str
    name: str
    names: Dict[str, str] = field(default_factory=dict)  # lang_code -> name
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
            raise ValueError("Organisation identifier is required")
        if not self.name:
            raise ValueError("Organisation name is required")

        # Ensure primary name is in names dict
        if not self.names:
            self.names = {"": self.name}  # Empty string for default language
        elif "" not in self.names and (not self.xml_lang or self.xml_lang not in self.names):
            self.names[self.xml_lang or ""] = self.name


class IatiOrganisationXMLGenerator:
    """
    Generator for IATI organisation XML files.

    This class generates IATI-compliant XML files for organisations according
    to the IATI organisation standard version 2.03.
    """

    def __init__(self, iati_version: str = "2.03"):
        """
        Initialize the XML generator.

        Args:
            iati_version: IATI standard version (default: 2.03)
        """
        self.iati_version = iati_version

    def build_root_element(self) -> ET.Element:
        """
        Create the root iati-organisations element.

        Returns:
            ET.Element: The root element with proper attributes
        """
        root = ET.Element("iati-organisations")
        _set_attribute(root, "version", self.iati_version)
        _set_attribute(
            root, "generated-datetime",
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        # Add XML namespace references
        _set_attribute(root, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        _set_attribute(
            root, "xmlns:xsi",
            "http://www.w3.org/2001/XMLSchema-instance"
        )

        return root

    def add_organisation(self, root: ET.Element, record: OrganisationRecord) -> ET.Element:
        """
        Add an organisation to the XML root element.

        Args:
            root: The root iati-organisations element
            record: Organisation data to add

        Returns:
            ET.Element: The created organisation element
        """
        org_el = ET.SubElement(root, "iati-organisation")
        _set_attribute(
            org_el, "last-updated-datetime",
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        # Use the preserved xml:lang from the record
        _set_attribute(org_el, "xml:lang", record.xml_lang or "en")

        # Add default currency if available
        if record.default_currency:
            _set_attribute(org_el, "default-currency", record.default_currency)

        # Add identifier
        oid = ET.SubElement(org_el, "organisation-identifier")
        oid.text = record.org_identifier

        # Add name with multiple narratives
        name_el = ET.SubElement(org_el, "name")
        if record.names:
            for lang_code, name_text in record.names.items():
                if name_text and name_text.strip():
                    narr = ET.SubElement(name_el, "narrative")
                    narr.text = name_text.strip()
                    if lang_code and lang_code.strip():
                        narr.set("xml:lang", lang_code.strip())
        else:
            # Fallback to single name
            _add_narrative(name_el, record.name)

        # Add reporting-org
        if record.reporting_org_ref or record.reporting_org_type or record.reporting_org_name:
            rep_org = ET.SubElement(org_el, "reporting-org")
            _set_attribute(rep_org, "ref", record.reporting_org_ref)
            _set_attribute(rep_org, "type", record.reporting_org_type)
            # Use the preserved language for reporting org narrative
            _add_narrative(rep_org, record.reporting_org_name, record.reporting_org_lang)

        # Add budgets
        for budget in record.budgets:
            self._add_budget(org_el, budget)

        # Add expenditures
        for expenditure in record.expenditures:
            self._add_expenditure(org_el, expenditure)

        # Add document links
        for document in record.documents:
            self._add_document_link(org_el, document)

        return org_el

    def _add_budget(self, org_el: ET.Element, budget: OrganisationBudget) -> None:
        """
        Add a budget element to the organisation.

        Args:
            org_el: Parent organisation element
            budget: Budget data to add
        """
        budget_el = ET.SubElement(org_el, budget.kind)
        _set_attribute(budget_el, "status", budget.status)

        # Add recipient information based on budget kind
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

        # Add period information
        if budget.period_start:
            period_start = ET.SubElement(budget_el, "period-start")
            _set_attribute(period_start, "iso-date", budget.period_start)

        if budget.period_end:
            period_end = ET.SubElement(budget_el, "period-end")
            _set_attribute(period_end, "iso-date", budget.period_end)

        # Add value
        if budget.value:
            value_el = ET.SubElement(budget_el, "value")
            value_el.text = str(budget.value)
            _set_attribute(value_el, "currency", budget.currency)
            _set_attribute(value_el, "value-date", budget.value_date or budget.period_start)

        # Add budget lines if present
        for line in budget.budget_lines:
            if "value" in line:
                line_el = ET.SubElement(budget_el, "budget-line")
                _set_attribute(line_el, "ref", line.get("ref", ""))

                # Add budget line value
                value_el = ET.SubElement(line_el, "value")
                value_el.text = str(line["value"])
                _set_attribute(value_el, "currency", line.get("currency", budget.currency))
                _set_attribute(value_el, "value-date", line.get("value_date", budget.value_date))

                # Add narrative if present
                if "narrative" in line:
                    _add_narrative(line_el, line["narrative"], line.get("lang", ""))

    def _add_expenditure(self, org_el: ET.Element, expenditure: OrganisationExpenditure) -> None:
        """
        Add a total-expenditure element to the organisation.

        Args:
            org_el: Parent organisation element
            expenditure: Expenditure data to add
        """
        exp_el = ET.SubElement(org_el, "total-expenditure")

        # Add period information
        period_start = ET.SubElement(exp_el, "period-start")
        _set_attribute(period_start, "iso-date", expenditure.period_start)

        period_end = ET.SubElement(exp_el, "period-end")
        _set_attribute(period_end, "iso-date", expenditure.period_end)

        # Add value
        value_el = ET.SubElement(exp_el, "value")
        value_el.text = str(expenditure.value)
        _set_attribute(value_el, "currency", expenditure.currency)
        _set_attribute(value_el, "value-date", expenditure.value_date or expenditure.period_start)

        # Add expense lines if present
        for line in expenditure.expense_lines:
            if "value" in line:
                line_el = ET.SubElement(exp_el, "expense-line")
                _set_attribute(line_el, "ref", line.get("ref", ""))

                # Add expense line value
                value_el = ET.SubElement(line_el, "value")
                value_el.text = str(line["value"])
                _set_attribute(value_el, "currency", line.get("currency", expenditure.currency))
                _set_attribute(value_el, "value-date", line.get("value_date", expenditure.value_date))

                # Add narrative if present
                if "narrative" in line:
                    _add_narrative(line_el, line["narrative"], line.get("lang", ""))

    def _add_document_link(self, org_el: ET.Element, document: OrganisationDocument) -> None:
        """
        Add a document-link element to the organisation.

        Args:
            org_el: Parent organisation element
            document: Document data to add
        """
        doc_el = ET.SubElement(org_el, "document-link")
        _set_attribute(doc_el, "url", document.url)
        _set_attribute(doc_el, "format", document.format)

        # Add title
        if document.title:
            title_el = ET.SubElement(doc_el, "title")
            _add_narrative(title_el, document.title)

        # Add category
        if document.category_code:
            category = ET.SubElement(doc_el, "category")
            _set_attribute(category, "code", document.category_code)

        # Add language
        if document.language:
            language = ET.SubElement(doc_el, "language")
            _set_attribute(language, "code", document.language)

        # Add document date
        if document.document_date:
            doc_date = ET.SubElement(doc_el, "document-date")
            _set_attribute(doc_date, "iso-date", document.document_date)

    def to_string(self, root: ET.Element) -> str:
        """
        Convert the XML to a properly formatted string.

        Args:
            root: Root XML element

        Returns:
            str: Pretty-printed XML string with proper headers
        """
        xml_string = _pretty_xml(root)

        # Add generator comment after XML declaration
        repo_url = "https://github.com/okfn/okfn-iati"
        comment = f"<!-- Generated by OKFN-IATI Organisation XML Generator: {repo_url} -->"

        xml_declaration_end = xml_string.find("?>") + 2
        xml_string = xml_string[:xml_declaration_end] + "\n" + comment + xml_string[xml_declaration_end:]

        return xml_string

    def save_to_file(self, root: ET.Element, file_path: Union[str, Path]) -> None:
        """
        Save the XML to a file.

        Args:
            root: Root XML element
            file_path: Path where to save the XML file
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_string(root))


class IatiOrganisationCSVConverter:
    """
    Converter for IATI organisation data between CSV/Excel and XML formats.

    This class provides methods to:
    1. Read organisation data from CSV/Excel files
    2. Generate IATI-compliant organisation XML files
    3. Process multiple organisation files in batch
    """

    # Define field name mappings for CSV columns
    FIELD_MAPPINGS = {
        "org_identifier": ["organisation identifier", "organization identifier",
                           "organisation-identifier", "org identifier",
                           "org_id", "organisation id", "organization id"],
        "name": ["name", "organisation name", "organization name", "nombre"],
        "reporting_org_ref": ["reporting org ref", "reporting-org ref", "reporting_org_ref", "reporting org identifier"],
        "reporting_org_type": ["reporting org type", "reporting-org type", "reporting_org_type", "reporting type"],
        "reporting_org_name": ["reporting org name", "reporting-org name", "reporting_org_name", "reporting name"],

        # Budget fields
        "budget_kind": ["budget kind", "budget_type", "budget type", "tipo presupuesto"],
        "budget_status": ["budget status", "status", "estado"],
        "budget_start": ["period start", "budget period start", "period-start", "inicio"],
        "budget_end": ["period end", "budget period end", "period-end", "fin"],
        "budget_value": ["budget value", "value", "monto", "valor"],
        "budget_currency": ["currency", "moneda"],
        "budget_value_date": ["value date", "value-date", "fecha valor"],

        # Recipient fields
        "recipient_org_ref": ["recipient org ref", "recipient-org ref", "recipient_org_ref"],
        "recipient_org_type": ["recipient org type", "recipient-org type", "recipient_org_type"],
        "recipient_org_name": ["recipient org name", "recipient-org name", "recipient_org_name"],
        "recipient_country_code": [
            "recipient country code", "recipient-country code",
            "recipient_country_code", "pais codigo"
        ],
        "recipient_region_code": [
            "recipient region code", "recipient-region code",
            "recipient_region_code", "region codigo"
        ],
        "recipient_region_vocabulary": [
            "recipient region vocabulary", "recipient-region vocabulary",
            "recipient_region_vocabulary", "region vocab"
        ],

        # Expenditure fields
        "expenditure_start": [
            "expenditure start", "expenditure period start",
            "expenditure-start", "gasto inicio"
        ],
        "expenditure_end": [
            "expenditure end", "expenditure period end",
            "expenditure-end", "gasto fin"
        ],
        "expenditure_value": ["expenditure value", "expenditure", "gasto valor"],
        "expenditure_currency": ["expenditure currency", "gasto moneda"],
        "expenditure_value_date": ["expenditure date", "gasto fecha"],

        # Document fields
        "document_url": [
            "document url", "document-link url", "url documento",
            "doc url", "url"
        ],
        "document_format": ["document format", "format", "mime", "formato"],
        "document_title": ["document title", "title", "titulo"],
        "document_category": ["document category", "category", "categoria"],
        "document_language": ["document language", "language", "idioma"],
        "document_date": ["document date", "date", "fecha documento"]
    }

    def __init__(self):
        """Initialize the converter."""
        self.xml_generator = IatiOrganisationXMLGenerator()

    def read_from_file(self, file_path: Union[str, Path]) -> OrganisationRecord:
        """
        Read organisation data from a CSV or Excel file.

        Args:
            file_path: Path to CSV or Excel file

        Returns:
            OrganisationRecord: Organisation data from the first row of the file

        Raises:
            ValueError: If required fields are missing or file format is unsupported
        """
        # Determine file type and read the first row
        file_path = Path(file_path)
        row = self._read_first_row(file_path)

        # Extract organisation data
        org_identifier = _get_field(row, self.FIELD_MAPPINGS["org_identifier"])
        name = _get_field(row, self.FIELD_MAPPINGS["name"])

        if not org_identifier or not name:
            raise ValueError("Missing required 'organisation identifier' or 'name' in the file")

        # Extract xml_lang
        xml_lang = row.get("xml_lang")

        # If completely missing, use default language ("en")
        if xml_lang is None or not xml_lang.strip():
            logger.warning(
                f"Missing 'xml_lang' in {file_path.name}, using default 'en'"
            )
            xml_lang = "en"

        # Extract default currency if available
        default_currency = row.get("default_currency") or row.get("currency") or "USD"

        # Create organisation record
        record = OrganisationRecord(
            org_identifier=org_identifier,
            name=name,
            reporting_org_ref=_get_field(row, self.FIELD_MAPPINGS["reporting_org_ref"]),
            reporting_org_type=_get_field(row, self.FIELD_MAPPINGS["reporting_org_type"]),
            reporting_org_name=_get_field(row, self.FIELD_MAPPINGS["reporting_org_name"]),
            xml_lang=xml_lang,
            default_currency=default_currency
        )

        # Extract budget if present
        budget_kind = _get_field(row, self.FIELD_MAPPINGS["budget_kind"])
        budget_value = _get_field(row, self.FIELD_MAPPINGS["budget_value"])

        if budget_kind and budget_value:
            # Determine actual budget kind if needed
            if budget_kind.lower() in ["total", "total-budget", "total budget"]:
                budget_kind = "total-budget"
            elif any(_get_field(row, self.FIELD_MAPPINGS[f]) for f in [
                "recipient_org_ref", "recipient_org_name"
            ]):
                budget_kind = "recipient-org-budget"
            elif _get_field(row, self.FIELD_MAPPINGS["recipient_country_code"]):
                budget_kind = "recipient-country-budget"
            elif _get_field(row, self.FIELD_MAPPINGS["recipient_region_code"]):
                budget_kind = "recipient-region-budget"

            # Create budget
            budget = OrganisationBudget(
                kind=budget_kind,
                status=_get_field(row, self.FIELD_MAPPINGS["budget_status"], "2"),  # Default to committed
                period_start=_get_field(row, self.FIELD_MAPPINGS["budget_start"]),
                period_end=_get_field(row, self.FIELD_MAPPINGS["budget_end"]),
                value=budget_value,
                currency=_get_field(row, self.FIELD_MAPPINGS["budget_currency"], "USD"),
                value_date=_get_field(row, self.FIELD_MAPPINGS["budget_value_date"]),
                recipient_org_ref=_get_field(row, self.FIELD_MAPPINGS["recipient_org_ref"]),
                recipient_org_type=_get_field(row, self.FIELD_MAPPINGS["recipient_org_type"]),
                recipient_org_name=_get_field(row, self.FIELD_MAPPINGS["recipient_org_name"]),
                recipient_country_code=_get_field(row, self.FIELD_MAPPINGS["recipient_country_code"]),
                recipient_region_code=_get_field(row, self.FIELD_MAPPINGS["recipient_region_code"]),
                recipient_region_vocabulary=_get_field(row, self.FIELD_MAPPINGS["recipient_region_vocabulary"])
            )
            record.budgets.append(budget)

        # Extract expenditure if present
        expenditure_value = _get_field(row, self.FIELD_MAPPINGS["expenditure_value"])
        if expenditure_value:
            expenditure = OrganisationExpenditure(
                period_start=_get_field(row, self.FIELD_MAPPINGS["expenditure_start"]),
                period_end=_get_field(row, self.FIELD_MAPPINGS["expenditure_end"]),
                value=expenditure_value,
                currency=_get_field(row, self.FIELD_MAPPINGS["expenditure_currency"], "USD"),
                value_date=_get_field(row, self.FIELD_MAPPINGS["expenditure_value_date"])
            )
            record.expenditures.append(expenditure)

        # Extract document if present
        document_url = _get_field(row, self.FIELD_MAPPINGS["document_url"])
        if document_url:
            document = OrganisationDocument(
                url=document_url,
                format=_get_field(row, self.FIELD_MAPPINGS["document_format"], "text/html"),
                title=_get_field(row, self.FIELD_MAPPINGS["document_title"], "Supporting document"),
                category_code=_get_field(row, self.FIELD_MAPPINGS["document_category"], "A01"),  # Default to Annual Report
                language=_get_field(row, self.FIELD_MAPPINGS["document_language"], "en"),
                document_date=_get_field(row, self.FIELD_MAPPINGS["document_date"])
            )
            record.documents.append(document)

        return record

    def _read_first_row(self, file_path: Path) -> Dict[str, Any]:
        """
        Read the first data row from a CSV or Excel file.

        Args:
            file_path: Path to file

        Returns:
            Dict: First row as a dictionary

        Raises:
            ValueError: If file format is unsupported or file is empty
        """
        # Handle Excel files if pandas is available
        if PANDAS_AVAILABLE and file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            if df.empty:
                raise ValueError(f"File {file_path} is empty")

            # Convert first row to dictionary
            row = df.iloc[0].to_dict()
            # Normalize row keys and values
            return {
                str(k).strip(): ("" if pd.isna(v) else str(v).strip())
                for k, v in row.items()
            }

        # Handle CSV files
        elif file_path.suffix.lower() == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                try:
                    # Get first row
                    row = next(reader)
                    # Normalize row
                    return {
                        str(k).strip(): ("" if v is None else str(v).strip())
                        for k, v in row.items()
                    }
                except StopIteration:
                    raise ValueError(f"File {file_path} has no data rows")

        else:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. "
                "Use CSV or Excel (.xlsx/.xls) files."
            )

    def convert_to_xml(self,
                       input_file: Union[str, Path],
                       output_file: Union[str, Path]) -> str:
        """
        Convert organisation data from CSV/Excel to IATI XML.

        Args:
            input_file: Path to input CSV or Excel file
            output_file: Path to output XML file

        Returns:
            str: Path to generated XML file

        Raises:
            ValueError: If conversion fails
        """
        try:
            # Read organisation data
            record = self.read_from_file(input_file)

            # Generate XML
            root = self.xml_generator.build_root_element()
            self.xml_generator.add_organisation(root, record)

            # Save XML to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.xml_generator.save_to_file(root, output_path)

            logger.info(f"Successfully generated IATI organisation XML: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert {input_file} to IATI XML: {str(e)}")
            raise ValueError(f"Conversion failed: {str(e)}")

    def read_multiple_from_folder(self, folder_path: Union[str, Path]) -> List[OrganisationRecord]:
        """
        Read organisation data from multiple CSV/Excel files in a folder.

        Args:
            folder_path: Path to folder containing CSV or Excel files

        Returns:
            List[OrganisationRecord]: List of organisation records from all files

        Raises:
            ValueError: If folder doesn't exist or contains no valid files
        """
        folder_path = Path(folder_path)

        if not folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        # Find all CSV and Excel files
        file_patterns = ["*.csv", "*.xlsx", "*.xls"]
        files = []
        for pattern in file_patterns:
            files.extend(folder_path.glob(pattern))

        if not files:
            raise ValueError(f"No CSV or Excel files found in folder: {folder_path}")

        organisations = []
        processed_files = []
        failed_files = []

        for file_path in sorted(files):
            try:
                logger.info(f"Processing organisation file: {file_path.name}")
                record = self.read_from_file(file_path)
                organisations.append(record)
                processed_files.append(file_path.name)
            except Exception as e:
                logger.warning(f"Failed to process {file_path.name}: {str(e)}")
                failed_files.append((file_path.name, str(e)))
                continue

        if not organisations:
            raise ValueError(
                f"No valid organisation data found in folder {folder_path}. "
                f"Failed files: {failed_files}"
            )

        logger.info(
            f"Successfully processed {len(processed_files)} organisation files. "
            f"Failed: {len(failed_files)}"
        )

        if failed_files:
            logger.warning(f"Failed to process files: {failed_files}")

        return organisations

    def convert_folder_to_xml(
            self,
            input_folder: Union[str, Path],
            output_file: Union[str, Path]
    ) -> str:
        """
        Convert multiple organisation CSV/Excel files to a single IATI XML file.

        Args:
            input_folder: Path to folder containing CSV or Excel files
            output_file: Path to output XML file

        Returns:
            str: Path to generated XML file

        Raises:
            ValueError: If conversion fails
        """
        try:
            # Read all organisation records from folder
            records = self.read_multiple_from_folder(input_folder)

            # Generate XML with all organisations
            root = self.xml_generator.build_root_element()

            for record in records:
                self.xml_generator.add_organisation(root, record)

            # Save XML to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.xml_generator.save_to_file(root, output_path)

            logger.info(
                f"Successfully generated IATI organisation XML with {len(records)} organisations: {output_path}"
            )
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert folder {input_folder} to IATI XML: {str(e)}")
            raise ValueError(f"Folder conversion failed: {str(e)}")

    def validate_organisation_identifiers(self, records: List[OrganisationRecord]) -> List[str]:
        """
        Check for duplicate organisation identifiers in a list of records.

        Args:
            records: List of organisation records to validate

        Returns:
            List of duplicate organisation identifiers found
        """
        seen_identifiers = set()
        duplicates = set()

        for record in records:
            identifier = record.org_identifier
            if identifier in seen_identifiers:
                duplicates.add(identifier)
            else:
                seen_identifiers.add(identifier)

        return list(duplicates)

    def generate_template(self, output_file: Union[str, Path], with_examples: bool = True) -> None:
        """
        Generate a CSV template for IATI organisation data.

        Args:
            output_file: Path to output CSV template file
            with_examples: Whether to include example data

        Raises:
            ValueError: If file creation fails
        """
        # Define template columns
        columns = [
            # Basic organisation info
            "Organisation Identifier",
            "Name",
            "Reporting Org Ref",
            "Reporting Org Type",
            "Reporting Org Name",

            # Budget info
            "Budget Kind",
            "Budget Status",
            "Budget Period Start",
            "Budget Period End",
            "Budget Value",
            "Currency",
            "Value Date",

            # Recipient info
            "Recipient Org Ref",
            "Recipient Org Type",
            "Recipient Org Name",
            "Recipient Country Code",
            "Recipient Region Code",
            "Recipient Region Vocabulary",

            # Document info
            "Document URL",
            "Document Format",
            "Document Title",
            "Document Category",
            "Document Language",
            "Document Date",

            # Expenditure info
            "Expenditure Period Start",
            "Expenditure Period End",
            "Expenditure Value",
            "Expenditure Currency"
        ]

        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)

                # Add example row if requested
                if with_examples:
                    writer.writerow([
                        "XM-DAC-46002",  # Organisation Identifier
                        "Sample Organisation",  # Name
                        "XM-DAC-46002",  # Reporting Org Ref
                        "40",  # Reporting Org Type
                        "Sample Organisation",  # Reporting Org Name
                        "total-budget",  # Budget Kind
                        "2",  # Budget Status
                        "2025-01-01",  # Budget Period Start
                        "2025-12-31",  # Budget Period End
                        "1000000",  # Budget Value
                        "USD",  # Currency
                        "2025-01-01",  # Value Date
                        "",  # Recipient Org Ref
                        "",  # Recipient Org Type
                        "",  # Recipient Org Name
                        "",  # Recipient Country Code
                        "",  # Recipient Region Code
                        "",  # Recipient Region Vocabulary
                        "https://example.org/annual-report",  # Document URL
                        "text/html",  # Document Format
                        "Annual Report",  # Document Title
                        "A01",  # Document Category
                        "en",  # Document Language
                        "2025-01-01",  # Document Date
                        "2025-01-01",  # Expenditure Period Start
                        "2025-12-31",  # Expenditure Period End
                        "950000",  # Expenditure Value
                        "USD"  # Expenditure Currency
                    ])

            logger.info(f"Generated IATI organisation template: {output_path}")

        except Exception as e:
            logger.error(f"Failed to create template {output_file}: {str(e)}")
            raise ValueError(f"Template creation failed: {str(e)}")


class IatiOrganisationMultiCsvConverter:
    """
    Multi-CSV converter for IATI organisation data.

    This class converts between IATI organisation XML and multiple CSV files,
    similar to the activity multi-CSV converter but for organisation data.
    """

    def __init__(self):
        """Initialize the multi-CSV converter."""
        self.xml_generator = IatiOrganisationXMLGenerator()

    def xml_to_csv_folder(
        self,
        xml_input: Union[str, Path],
        output_folder: Union[str, Path]
    ) -> bool:
        """
        Convert IATI organisation XML to multiple CSV files in a folder.

        Args:
            xml_input: Path to input XML file
            output_folder: Path to output folder for CSV files

        Returns:
            bool: True if conversion successful
        """
        try:
            # Parse XML
            xml_path = Path(xml_input)
            if not xml_path.exists():
                raise ValueError(f"XML file not found: {xml_input}")

            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Create output folder
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)

            # Extract organisation data
            organisations_data = []
            names_data = []
            budgets_data = []
            expenditures_data = []
            documents_data = []

            for org_elem in root.findall('.//iati-organisation'):
                # Extract basic organisation info
                org_data = self._extract_organisation_basic_info(org_elem)
                organisations_data.append(org_data)

                # Extract names
                org_names = self._extract_organisation_names(org_elem, org_data['organisation_identifier'])
                names_data.extend(org_names)

                # Extract budgets
                org_budgets = self._extract_organisation_budgets(org_elem, org_data['organisation_identifier'])
                budgets_data.extend(org_budgets)

                # Extract expenditures
                org_expenditures = self._extract_organisation_expenditures(org_elem, org_data['organisation_identifier'])
                expenditures_data.extend(org_expenditures)

                # Extract documents
                org_documents = self._extract_organisation_documents(org_elem, org_data['organisation_identifier'])
                documents_data.extend(org_documents)

            # Write CSV files
            self._write_organisations_csv(organisations_data, output_path / "organisations.csv")

            # Only create names.csv if there are multiple names per organisation
            multi_name_count = 0
            for org_id in {n["organisation_identifier"] for n in names_data}:
                names_for_org = [n for n in names_data if n["organisation_identifier"] == org_id]
                if len(names_for_org) > 1:
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
            logger.error(f"Failed to convert XML to CSV folder: {str(e)}")
            return False

    def csv_folder_to_xml(  # noqa: C901
        self,
        input_folder: Union[str, Path],
        xml_output: Union[str, Path]
    ) -> bool:
        """
        Convert multiple CSV files to IATI organisation XML.

        Args:
            input_folder: Path to folder containing CSV files
            xml_output: Path to output XML file

        Returns:
            bool: True if conversion successful
        """
        try:
            folder_path = Path(input_folder)
            if not folder_path.exists():
                raise ValueError(f"Input folder not found: {input_folder}")

            # Read CSV files
            organisations = self._read_organisations_csv(folder_path / "organisations.csv")
            names = self._read_names_csv(folder_path / "names.csv") if (folder_path / "names.csv").exists() else []
            budgets = self._read_budgets_csv(folder_path / "budgets.csv") if (folder_path / "budgets.csv").exists() else []
            expenditures = self._read_expenditures_csv(
                folder_path / "expenditures.csv"
            ) if (folder_path / "expenditures.csv").exists() else []
            documents = self._read_documents_csv(
                folder_path / "documents.csv"
            ) if (folder_path / "documents.csv").exists() else []

            # Group data by organisation identifier
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

            # Associate names, budgets, expenditures, and documents with organisations
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

            # Create organisation records
            records = []
            for org_id, data in org_data_map.items():
                record = self._create_organisation_record_from_csv_data(data)
                records.append(record)

            # Generate XML
            root = self.xml_generator.build_root_element()
            for record in records:
                self.xml_generator.add_organisation(root, record)

            # Save XML
            output_path = Path(xml_output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.xml_generator.save_to_file(root, output_path)

            logger.info(f"Successfully converted CSV folder to organisation XML: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to convert CSV folder to XML: {str(e)}")
            return False

    def generate_csv_templates(
        self,
        output_folder: Union[str, Path],
        include_examples: bool = True
    ) -> None:
        """
        Generate CSV template files for organisation data.

        Args:
            output_folder: Path to output folder
            include_examples: Whether to include example data
        """
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate organisations.csv template
        org_columns = [
            "organisation_identifier", "name", "reporting_org_ref",
            "reporting_org_type", "reporting_org_name", "reporting_org_lang",
            "default_currency", "xml_lang"
        ]

        with open(output_path / "organisations.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(org_columns)

            if include_examples:
                writer.writerow([
                    "XM-DAC-46002", "Sample Organisation", "XM-DAC-46002",
                    "40", "Sample Organisation", "en", "USD", "en"
                ])

        # Generate names.csv template
        name_columns = [
            'organisation_identifier', 'language', 'name'
        ]

        with open(output_path / "names.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(name_columns)

            if include_examples:
                writer.writerow([
                    'XM-DAC-46002', '', 'Central American Bank for Economic Integration'
                ])
                writer.writerow([
                    'XM-DAC-46002', 'es', 'Banco Centroamericano de Integración Económica'
                ])

        # Generate budgets.csv template
        budget_columns = [
            'organisation_identifier', 'budget_kind', 'budget_status',
            'period_start', 'period_end', 'value', 'currency', 'value_date',
            'recipient_org_ref', 'recipient_org_type', 'recipient_org_name',
            'recipient_country_code', 'recipient_region_code', 'recipient_region_vocabulary'
        ]

        with open(output_path / "budgets.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(budget_columns)

            if include_examples:
                writer.writerow([
                    'XM-DAC-46002', 'total-budget', '2',
                    '2025-01-01', '2025-12-31', '1000000', 'USD', '2025-01-01',
                    '', '', '', '', '', ''
                ])

        # Generate expenditures.csv template
        expenditure_columns = [
            'organisation_identifier', 'period_start', 'period_end',
            'value', 'currency', 'value_date'
        ]

        with open(output_path / "expenditures.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(expenditure_columns)

            if include_examples:
                writer.writerow([
                    'XM-DAC-46002', '2024-01-01', '2024-12-31',
                    '950000', 'USD', '2024-01-01'
                ])

        # Generate documents.csv template
        document_columns = [
            'organisation_identifier', 'url', 'format', 'title',
            'category_code', 'language', 'document_date'
        ]

        with open(output_path / "documents.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(document_columns)

            if include_examples:
                writer.writerow([
                    'XM-DAC-46002', 'https://example.org/annual-report.pdf',
                    'application/pdf', 'Annual Report 2024', 'A01', 'en', '2025-01-01'
                ])

        logger.info(f"Generated organisation CSV templates in: {output_path}")

    def _extract_organisation_basic_info(self, org_elem: ET.Element) -> Dict[str, str]:
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

    def _extract_organisation_names(self, org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
        """Extract organisation names in multiple languages."""
        names = []

        name_elem = org_elem.find('name')
        if name_elem is not None:
            narratives = name_elem.findall('narrative')
            for narr in narratives:
                if narr.text:
                    name_data = {
                        'organisation_identifier': org_identifier,
                        'language': narr.get('{http://www.w3.org/XML/1998/namespace}lang', ''),
                        'name': narr.text
                    }
                    names.append(name_data)

        return names

    def _extract_organisation_budgets(self, org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:  # noqa: C901
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
                budget_data['value'] = value_elem.text or ''
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

            # Extract recipient org info
            recip_org = budget_elem.find('recipient-org')
            if recip_org is not None:
                budget_data['recipient_org_ref'] = recip_org.get('ref', '')
                budget_data['recipient_org_type'] = recip_org.get('type', '')

                recip_name = recip_org.find('narrative')
                if recip_name is not None:
                    budget_data['recipient_org_name'] = recip_name.text

            # Extract period and value info (same as total budget)
            period_start = budget_elem.find('period-start')
            if period_start is not None:
                budget_data['period_start'] = period_start.get('iso-date', '')

            period_end = budget_elem.find('period-end')
            if period_end is not None:
                budget_data['period_end'] = period_end.get('iso-date', '')

            value_elem = budget_elem.find('value')
            if value_elem is not None:
                budget_data['value'] = value_elem.text or ''
                budget_data['currency'] = value_elem.get('currency', '')
                budget_data['value_date'] = value_elem.get('value-date', '')

            budgets.append(budget_data)

        # Add recipient-country-budget and recipient-region-budget similarly
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

            # Extract recipient country info
            recip_country = budget_elem.find('recipient-country')
            if recip_country is not None:
                budget_data['recipient_country_code'] = recip_country.get('code', '')

            # Extract period and value info
            period_start = budget_elem.find('period-start')
            if period_start is not None:
                budget_data['period_start'] = period_start.get('iso-date', '')

            period_end = budget_elem.find('period-end')
            if period_end is not None:
                budget_data['period_end'] = period_end.get('iso-date', '')

            value_elem = budget_elem.find('value')
            if value_elem is not None:
                budget_data['value'] = value_elem.text or ''
                budget_data['currency'] = value_elem.get('currency', '')
                budget_data['value_date'] = value_elem.get('value-date', '')

            budgets.append(budget_data)

        return budgets

    def _extract_organisation_expenditures(self, org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
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
                exp_data['value'] = value_elem.text or ''
                exp_data['currency'] = value_elem.get('currency', '')
                exp_data['value_date'] = value_elem.get('value-date', '')

            expenditures.append(exp_data)

        return expenditures

    def _extract_organisation_documents(self, org_elem: ET.Element, org_identifier: str) -> List[Dict[str, str]]:
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
                doc_data['title'] = title_elem.text

            category_elem = doc_elem.find('category')
            if category_elem is not None:
                doc_data['category_code'] = category_elem.get('code', '')

            lang_elem = doc_elem.find('language')
            if lang_elem is not None:
                doc_data['language'] = lang_elem.get('code', '')

            date_elem = doc_elem.find('document-date')
            if date_elem is not None:
                doc_data['document_date'] = date_elem.get('iso-date', '')

            documents.append(doc_data)

        return documents

    def _write_organisations_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write organisations data to CSV."""
        if not data:
            return

        columns = [
            'organisation_identifier', 'name', 'reporting_org_ref',
            'reporting_org_type', 'reporting_org_name', 'reporting_org_lang',
            'default_currency', 'xml_lang'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow({col: row.get(col, '') for col in columns})

    def _write_names_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write names data to CSV."""
        if not data:
            return

        columns = ['organisation_identifier', 'language', 'name']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow({col: row.get(col, '') for col in columns})

    def _write_budgets_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write budgets data to CSV."""
        if not data:
            return

        columns = [
            'organisation_identifier', 'budget_kind', 'budget_status',
            'period_start', 'period_end', 'value', 'currency', 'value_date',
            'recipient_org_ref', 'recipient_org_type', 'recipient_org_name',
            'recipient_country_code', 'recipient_region_code', 'recipient_region_vocabulary'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow({col: row.get(col, '') for col in columns})

    def _write_expenditures_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write expenditures data to CSV."""
        if not data:
            return

        columns = [
            'organisation_identifier', 'period_start', 'period_end',
            'value', 'currency', 'value_date'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow({col: row.get(col, '') for col in columns})

    def _write_documents_csv(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """Write documents data to CSV."""
        if not data:
            return

        columns = [
            'organisation_identifier', 'url', 'format', 'title',
            'category_code', 'language', 'document_date'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow({col: row.get(col, '') for col in columns})

    def _read_organisations_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read organisations CSV file."""
        organisations = []

        if not csv_path.exists():
            return organisations

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                organisations.append(dict(row))

        return organisations

    def _read_names_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read names CSV file."""
        names = []

        if not csv_path.exists():
            return names

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names.append(dict(row))

        return names

    def _read_budgets_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read budgets CSV file."""
        budgets = []

        if not csv_path.exists():
            return budgets

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                budgets.append(dict(row))

        return budgets

    def _read_expenditures_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read expenditures CSV file."""
        expenditures = []

        if not csv_path.exists():
            return expenditures

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenditures.append(dict(row))

        return expenditures

    def _read_documents_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """Read documents CSV file."""
        documents = []

        if not csv_path.exists():
            return documents

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                documents.append(dict(row))

        return documents

    def _create_organisation_record_from_csv_data(self, data: Dict[str, Any]) -> OrganisationRecord:
        """Create OrganisationRecord from CSV data."""
        basic_info = data['basic_info']

        # Parse multilingual names from names CSV data
        names_dict = {}
        for name_data in data['names']:
            lang = name_data.get('language', '')
            name_text = name_data.get('name', '')
            if name_text.strip():
                names_dict[lang] = name_text.strip()

        # Create basic record
        record = OrganisationRecord(
            org_identifier=basic_info['organisation_identifier'],
            name=basic_info['name'],
            names=names_dict,
            reporting_org_ref=basic_info.get('reporting_org_ref', ''),
            reporting_org_type=basic_info.get('reporting_org_type', ''),
            reporting_org_name=basic_info.get('reporting_org_name', ''),
            # Store language attributes for later use in XML generation
            reporting_org_lang=basic_info.get('reporting_org_lang', ''),
            xml_lang=basic_info.get('xml_lang', 'en'),
            default_currency=basic_info.get('default_currency', 'USD')
        )

        # Add budgets
        for budget_data in data['budgets']:
            if budget_data.get('value'):
                budget = OrganisationBudget(
                    kind=budget_data['budget_kind'],
                    status=budget_data.get('budget_status', '1'),
                    period_start=budget_data.get('period_start', ''),
                    period_end=budget_data.get('period_end', ''),
                    value=budget_data['value'],
                    currency=budget_data.get('currency', 'USD'),
                    value_date=budget_data.get('value_date', ''),
                    recipient_org_ref=budget_data.get('recipient_org_ref', ''),
                    recipient_org_type=budget_data.get('recipient_org_type', ''),
                    recipient_org_name=budget_data.get('recipient_org_name', ''),
                    recipient_country_code=budget_data.get('recipient_country_code', ''),
                    recipient_region_code=budget_data.get('recipient_region_code', ''),
                    recipient_region_vocabulary=budget_data.get('recipient_region_vocabulary', '')
                )
                record.budgets.append(budget)

        # Add expenditures
        for exp_data in data['expenditures']:
            if exp_data.get('value'):
                expenditure = OrganisationExpenditure(
                    period_start=exp_data['period_start'],
                    period_end=exp_data['period_end'],
                    value=exp_data['value'],
                    currency=exp_data.get('currency', 'USD'),
                    value_date=exp_data.get('value_date', '')
                )
                record.expenditures.append(expenditure)

        # Add documents
        for doc_data in data['documents']:
            if doc_data.get('url'):
                document = OrganisationDocument(
                    url=doc_data['url'],
                    format=doc_data.get('format', 'text/html'),
                    title=doc_data.get('title', ''),
                    category_code=doc_data.get('category_code', ''),
                    language=doc_data.get('language', ''),
                    document_date=doc_data.get('document_date', '')
                )
                record.documents.append(document)

        return record


# Update main function to include multi-CSV commands
def main():
    """Command line interface for converting organisation files."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert between IATI organisation data formats"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert CSV/Excel to IATI XML")
    convert_parser.add_argument("input", help="Input CSV/Excel file or folder")
    convert_parser.add_argument("output", help="Output XML file")
    convert_parser.add_argument(
        "--folder", action="store_true",
        help="Process all CSV/Excel files in input folder"
    )

    # Template command
    template_parser = subparsers.add_parser("template", help="Generate a CSV template")
    template_parser.add_argument("output", help="Output template file")
    template_parser.add_argument(
        "--no-examples", action="store_true",
        help="Don't include example data"
    )

    # Multi-CSV template command
    multi_template_parser = subparsers.add_parser("multi-template", help="Generate multi-CSV templates")
    multi_template_parser.add_argument("output_folder", help="Output folder for CSV templates")
    multi_template_parser.add_argument(
        "--no-examples", action="store_true",
        help="Don't include example data"
    )

    # XML to multi-CSV command
    xml_to_csv_parser = subparsers.add_parser("xml-to-csv-folder", help="Convert XML to CSV folder")
    xml_to_csv_parser.add_argument("input", help="Input XML file")
    xml_to_csv_parser.add_argument("output_folder", help="Output CSV folder")

    # Multi-CSV to XML command
    csv_to_xml_parser = subparsers.add_parser("csv-folder-to-xml", help="Convert CSV folder to XML")
    csv_to_xml_parser.add_argument("input_folder", help="Input CSV folder")
    csv_to_xml_parser.add_argument("output", help="Output XML file")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate organisation data")
    validate_parser.add_argument("input", help="Input CSV/Excel file or folder")
    validate_parser.add_argument(
        "--folder", action="store_true",
        help="Process all CSV/Excel files in input folder"
    )

    args = parser.parse_args()
    converter = IatiOrganisationCSVConverter()
    multi_converter = IatiOrganisationMultiCsvConverter()

    if args.command == "convert":
        if args.folder:
            output = converter.convert_folder_to_xml(args.input, args.output)
        else:
            output = converter.convert_to_xml(args.input, args.output)
        print(f"✅ Successfully converted to: {output}")

    elif args.command == "template":
        converter.generate_template(args.output, not args.no_examples)
        print(f"✅ Generated template: {args.output}")

    elif args.command == "multi-template":
        multi_converter.generate_csv_templates(args.output_folder, not args.no_examples)
        print(f"✅ Generated multi-CSV templates in: {args.output_folder}")

    elif args.command == "xml-to-csv-folder":
        success = multi_converter.xml_to_csv_folder(args.input, args.output_folder)
        if success:
            print(f"✅ Successfully converted XML to CSV folder: {args.output_folder}")
        else:
            print("❌ Failed to convert XML to CSV folder")

    elif args.command == "csv-folder-to-xml":
        success = multi_converter.csv_folder_to_xml(args.input_folder, args.output)
        if success:
            print(f"✅ Successfully converted CSV folder to XML: {args.output}")
        else:
            print("❌ Failed to convert CSV folder to XML")

    elif args.command == "validate":
        try:
            if args.folder:
                records = converter.read_multiple_from_folder(args.input)
            else:
                records = [converter.read_from_file(args.input)]

            # Check for duplicates
            duplicates = converter.validate_organisation_identifiers(records)

            if duplicates:
                print(f"❌ Found duplicate organisation identifiers: {duplicates}")
            else:
                print(f"✅ Validation passed for {len(records)} organisation(s)")

        except Exception as e:
            print(f"❌ Validation failed: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


"""
Examples
--------

General help:
    python src/okfn_iati/organisation_xml_generator.py --help

Generate a CSV template:
    python src/okfn_iati/organisation_xml_generator.py template test_template.csv

Convert single CSV to XML:
    python src/okfn_iati/organisation_xml_generator.py convert test_template.csv test_output.xml

Convert folder of CSV files to XML:
    python src/okfn_iati/organisation_xml_generator.py convert --folder /path/to/csv/folder output.xml

Validate organisation data:
    python src/okfn_iati/organisation_xml_generator.py validate --folder /path/to/csv/folder

Convert XML to multi-CSV folder:
    python src/okfn_iati/organisation_xml_generator.py xml-to-csv-folder input.xml output_folder
    Real life sample
    python src/okfn_iati/organisation_xml_generator.py xml-to-csv-folder \
        data-samples/organization-files/3fi-org.xml \
        data-samples/csv_folders_org/3fi
    and back to xml
    python src/okfn_iati/organisation_xml_generator.py csv-folder-to-xml \
        data-samples/csv_folders_org/3fi \
        data-samples/organization-files/3fi-org-back.xml

    Also
        python src/okfn_iati/organisation_xml_generator.py xml-to-csv-folder \
            data-samples/organization-files/ares-org.xml \
            data-samples/csv_folders_org/ares-org
        and back with
        python src/okfn_iati/organisation_xml_generator.py csv-folder-to-xml \
            data-samples/csv_folders_org/ares-org/ \
            data-samples/organization-files/ares-org-back.xml

    Also, for BE-BCE_KBO-0420656336
        python src/okfn_iati/organisation_xml_generator.py xml-to-csv-folder \
            data-samples/organization-files/BE-BCE_KBO-0420656336.xml \
            data-samples/csv_folders_org/BE-BCE_KBO-0420656336
        and back with
        python src/okfn_iati/organisation_xml_generator.py csv-folder-to-xml \
            data-samples/csv_folders_org/BE-BCE_KBO-0420656336/ \
            data-samples/organization-files/BE-BCE_KBO-0420656336-back.xml
"""
