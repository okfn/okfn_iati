"""
IATI Organisation XML Generator - Creates IATI-compliant organisation XML files.

This module generates IATI organisation XML files according to the IATI standard v2.03.
Organisation files contain information about the publishing organization and its budgets,
expenditure, and documents - distinct from activity files which describe projects.

References:
- https://iatistandard.org/en/guidance/standard-overview/organisation-infromation/
- https://iatistandard.org/en/iati-standard/203/organisation-standard/
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
    category_code: Optional[str] = None
    language: Optional[str] = None
    document_date: Optional[str] = None

@dataclass
class OrganisationRecord:
    """
    IATI Organisation record containing all organisation information.
    
    Args:
        org_identifier: Organisation identifier
        name: Organisation name
        reporting_org_ref: Reporting organisation reference
        reporting_org_type: Reporting organisation type
        reporting_org_name: Reporting organisation name
        budgets: List of organisation budgets
        expenditures: List of organisation expenditures
        documents: List of organisation document links
        total_expenditure: Total expenditure information
    """
    org_identifier: str
    name: str
    reporting_org_ref: Optional[str] = None
    reporting_org_type: Optional[str] = None
    reporting_org_name: Optional[str] = None
    budgets: List[OrganisationBudget] = field(default_factory=list)
    expenditures: List[OrganisationExpenditure] = field(default_factory=list)
    documents: List[OrganisationDocument] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.org_identifier:
            raise ValueError("Organisation identifier is required")
        if not self.name:
            raise ValueError("Organisation name is required")
            
        # Set defaults for reporting org if not provided
        if not self.reporting_org_ref:
            self.reporting_org_ref = self.org_identifier
        if not self.reporting_org_name:
            self.reporting_org_name = self.name
        if not self.reporting_org_type:
            self.reporting_org_type = "40"  # Default to "International NGO"

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
        _set_attribute(root, "generated-datetime", 
                     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        # Add XML namespace references
        _set_attribute(root, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        _set_attribute(root, "xmlns:xsi", 
                     "http://www.w3.org/2001/XMLSchema-instance")
        
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
        _set_attribute(org_el, "last-updated-datetime", 
                     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        _set_attribute(org_el, "xml:lang", "en")
        
        # Add identifier
        oid = ET.SubElement(org_el, "organisation-identifier")
        oid.text = record.org_identifier
        
        # Add name
        name_el = ET.SubElement(org_el, "name")
        _add_narrative(name_el, record.name)
        
        # Add reporting-org
        if record.reporting_org_ref or record.reporting_org_type or record.reporting_org_name:
            rep_org = ET.SubElement(org_el, "reporting-org")
            _set_attribute(rep_org, "ref", record.reporting_org_ref)
            _set_attribute(rep_org, "type", record.reporting_org_type)
            _add_narrative(rep_org, record.reporting_org_name)
        
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
    """
    
    # Define field name mappings for CSV columns
    FIELD_MAPPINGS = {
        "org_identifier": ["organisation identifier", "organization identifier", 
                           "organisation-identifier", "org identifier", 
                           "org_id", "organisation id", "organization id"],
        "name": ["name", "organisation name", "organization name", "nombre"],
        "reporting_org_ref": ["reporting org ref", "reporting-org ref", 
                             "reporting_org_ref", "reporting org identifier"],
        "reporting_org_type": ["reporting org type", "reporting-org type", 
                              "reporting_org_type", "reporting type"],
        "reporting_org_name": ["reporting org name", "reporting-org name", 
                              "reporting_org_name", "reporting name"],
        
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
        "recipient_country_code": ["recipient country code", "recipient-country code", 
                                  "recipient_country_code", "pais codigo"],
        "recipient_region_code": ["recipient region code", "recipient-region code", 
                                 "recipient_region_code", "region codigo"],
        "recipient_region_vocabulary": ["recipient region vocabulary", "recipient-region vocabulary", 
                                       "recipient_region_vocabulary", "region vocab"],
        
        # Expenditure fields
        "expenditure_start": ["expenditure start", "expenditure period start", 
                             "expenditure-start", "gasto inicio"],
        "expenditure_end": ["expenditure end", "expenditure period end", 
                           "expenditure-end", "gasto fin"],
        "expenditure_value": ["expenditure value", "expenditure", "gasto valor"],
        "expenditure_currency": ["expenditure currency", "gasto moneda"],
        "expenditure_value_date": ["expenditure date", "gasto fecha"],
        
        # Document fields
        "document_url": ["document url", "document-link url", "url documento", 
                        "doc url", "url"],
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
        
        # Create organisation record
        record = OrganisationRecord(
            org_identifier=org_identifier,
            name=name,
            reporting_org_ref=_get_field(row, self.FIELD_MAPPINGS["reporting_org_ref"]),
            reporting_org_type=_get_field(row, self.FIELD_MAPPINGS["reporting_org_type"]),
            reporting_org_name=_get_field(row, self.FIELD_MAPPINGS["reporting_org_name"])
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

def main():
    """Command line interface for converting organisation files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert between IATI organisation data formats"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert CSV/Excel to IATI XML")
    convert_parser.add_argument("input", help="Input CSV or Excel file")
    convert_parser.add_argument("output", help="Output XML file")
    
    # Template command
    template_parser = subparsers.add_parser("template", help="Generate a CSV template")
    template_parser.add_argument("output", help="Output template file")
    template_parser.add_argument("--no-examples", action="store_true", 
                               help="Don't include example data")
    
    args = parser.parse_args()
    converter = IatiOrganisationCSVConverter()
    
    if args.command == "convert":
        output = converter.convert_to_xml(args.input, args.output)
        print(f"✅ Successfully converted to: {output}")
    
    elif args.command == "template":
        converter.generate_template(args.output, not args.no_examples)
        print(f"✅ Generated template: {args.output}")
    
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

Convert CSV to XML:
    python src/okfn_iati/organisation_xml_generator.py convert test_template.csv test_output.xml
"""
