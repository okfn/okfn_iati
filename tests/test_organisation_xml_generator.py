import unittest
import tempfile
from pathlib import Path
import csv
import xml.etree.ElementTree as ET

from okfn_iati.organisation_xml_generator import (
    IatiOrganisationCSVConverter,
    IatiOrganisationXMLGenerator,
    OrganisationRecord,
)


class TestOrganisationXMLGenerator(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory and files for testing."""
        self.converter = IatiOrganisationCSVConverter()
        self.generator = IatiOrganisationXMLGenerator()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_file = Path(self.temp_dir.name) / "test_org.csv"
        self.xml_file = Path(self.temp_dir.name) / "test_org.xml"

        # Generate CSV template with example data
        self.converter.generate_template(self.csv_file, with_examples=True)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_csv_template_generated(self):
        """Check that the CSV file is generated."""
        self.assertTrue(self.csv_file.exists(), "CSV file was not created")

    def test_convert_csv_to_xml(self):
        """Convert CSV to XML and validate basic content."""
        output_path = self.converter.convert_to_xml(self.csv_file, self.xml_file)
        self.assertTrue(Path(output_path).exists(), "XML file was not created")

        # Read the content of the generated XML
        with open(output_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Check that basic IATI elements are present
        self.assertIn("<iati-organisations", xml_content)
        self.assertIn("<iati-organisation", xml_content)
        self.assertIn("<organisation-identifier>", xml_content)

    def test_multiple_csv_files_to_xml(self):
        """Test converting multiple CSV files from a folder to XML."""
        # Create multiple CSV files
        csv_folder = Path(self.temp_dir.name) / "csv_files"
        csv_folder.mkdir()

        # Create first organisation file
        org1_file = csv_folder / "org1.csv"
        self._create_test_csv(org1_file, "XM-DAC-001", "Organization One")

        # Create second organisation file
        org2_file = csv_folder / "org2.csv"
        self._create_test_csv(org2_file, "XM-DAC-002", "Organization Two")

        # Create third organisation file
        org3_file = csv_folder / "org3.csv"
        self._create_test_csv(org3_file, "XM-DAC-003", "Organization Three")

        # Convert folder to XML
        output_path = self.converter.convert_folder_to_xml(csv_folder, self.xml_file)
        self.assertTrue(Path(output_path).exists(), "XML file was not created")

        # Parse and validate XML content
        tree = ET.parse(output_path)
        root = tree.getroot()

        # Check root element
        self.assertEqual(root.tag, "iati-organisations")

        # Check that all three organisations are present
        organisations = root.findall("iati-organisation")
        self.assertEqual(len(organisations), 3)

        # Check organisation identifiers
        identifiers = []
        for org in organisations:
            identifier_elem = org.find("organisation-identifier")
            self.assertIsNotNone(identifier_elem)
            identifiers.append(identifier_elem.text)

        expected_identifiers = ["XM-DAC-001", "XM-DAC-002", "XM-DAC-003"]
        self.assertEqual(sorted(identifiers), sorted(expected_identifiers))

    def test_empty_folder_raises_error(self):
        """Test that an empty folder raises an appropriate error."""
        empty_folder = Path(self.temp_dir.name) / "empty"
        empty_folder.mkdir()

        with self.assertRaises(ValueError) as context:
            self.converter.read_multiple_from_folder(empty_folder)

        self.assertIn("No CSV or Excel files found", str(context.exception))

    def test_nonexistent_folder_raises_error(self):
        """Test that a non-existent folder raises an error."""
        nonexistent_folder = Path(self.temp_dir.name) / "nonexistent"

        with self.assertRaises(ValueError) as context:
            self.converter.read_multiple_from_folder(nonexistent_folder)

        self.assertIn("Folder does not exist", str(context.exception))

    def test_duplicate_organisation_identifiers_validation(self):
        """Test validation of duplicate organisation identifiers."""
        # Create records with duplicate identifiers
        record1 = OrganisationRecord(
            org_identifier="XM-DAC-001",
            name="Organization One"
        )
        record2 = OrganisationRecord(
            org_identifier="XM-DAC-002",
            name="Organization Two"
        )
        record3 = OrganisationRecord(
            org_identifier="XM-DAC-001",  # Duplicate
            name="Organization One Duplicate"
        )

        records = [record1, record2, record3]
        duplicates = self.converter.validate_organisation_identifiers(records)

        self.assertEqual(len(duplicates), 1)
        self.assertIn("XM-DAC-001", duplicates)

    def test_organisation_with_budgets_and_expenditures(self):
        """Test organisation with multiple budgets and expenditures."""
        # Create test data with budgets and expenditures
        csv_file = Path(self.temp_dir.name) / "org_with_budgets.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Organisation Identifier", "Name", "Reporting Org Ref", "Reporting Org Type", "Reporting Org Name",
                "Budget Kind", "Budget Status", "Budget Period Start", "Budget Period End", "Budget Value", "Currency",
                "Expenditure Period Start", "Expenditure Period End", "Expenditure Value"
            ])
            writer.writerow([
                "XM-DAC-456", "Test Org with Budget", "XM-DAC-456", "40", "Test Org with Budget",
                "total-budget", "2", "2023-01-01", "2023-12-31", "1000000", "USD",
                "2022-01-01", "2022-12-31", "950000"
            ])

        # Convert to XML
        output_path = self.converter.convert_to_xml(csv_file, self.xml_file)

        # Parse and validate XML
        tree = ET.parse(output_path)
        root = tree.getroot()

        org = root.find("iati-organisation")
        self.assertIsNotNone(org)

        # Check budget
        budget = org.find("total-budget")
        self.assertIsNotNone(budget)
        self.assertEqual(budget.get("status"), "2")

        budget_value = budget.find("value")
        self.assertIsNotNone(budget_value)
        self.assertEqual(budget_value.text, "1000000")
        self.assertEqual(budget_value.get("currency"), "USD")

        # Check expenditure
        expenditure = org.find("total-expenditure")
        self.assertIsNotNone(expenditure)

        exp_value = expenditure.find("value")
        self.assertIsNotNone(exp_value)
        self.assertEqual(exp_value.text, "950000")

    def test_organisation_with_documents(self):
        """Test organisation with document links."""
        csv_file = Path(self.temp_dir.name) / "org_with_docs.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Organisation Identifier", "Name", "Document URL", "Document Format",
                "Document Title", "Document Category", "Document Language"
            ])
            writer.writerow([
                "XM-DAC-789", "Org with Docs", "https://example.org/report.pdf",
                "application/pdf", "Annual Report 2023", "A01", "en"
            ])

        # Convert to XML
        output_path = self.converter.convert_to_xml(csv_file, self.xml_file)

        # Parse and validate XML
        tree = ET.parse(output_path)
        root = tree.getroot()

        org = root.find("iati-organisation")
        self.assertIsNotNone(org)

        # Check document link
        doc_link = org.find("document-link")
        self.assertIsNotNone(doc_link)
        self.assertEqual(doc_link.get("url"), "https://example.org/report.pdf")
        self.assertEqual(doc_link.get("format"), "application/pdf")

        doc_title = doc_link.find("title/narrative")
        self.assertIsNotNone(doc_title)
        self.assertEqual(doc_title.text, "Annual Report 2023")

    def test_xml_schema_compliance(self):
        """Test that generated XML follows IATI organisation schema structure."""
        output_path = self.converter.convert_to_xml(self.csv_file, self.xml_file)

        # Parse XML
        tree = ET.parse(output_path)
        root = tree.getroot()

        # Check root element attributes
        self.assertEqual(root.tag, "iati-organisations")
        self.assertIsNotNone(root.get("version"))
        self.assertIsNotNone(root.get("generated-datetime"))

        # Check organisation structure
        org = root.find("iati-organisation")
        self.assertIsNotNone(org)
        self.assertIsNotNone(org.get("last-updated-datetime"))

        # Check xml:lang attribute is set
        xml_lang = org.get("{http://www.w3.org/XML/1998/namespace}lang")
        self.assertIsNotNone(xml_lang, "xml:lang attribute should be set on organisation element")
        self.assertEqual(xml_lang, "en", "xml:lang should be 'en'")

        # Required elements
        org_id = org.find("organisation-identifier")
        self.assertIsNotNone(org_id)
        self.assertTrue(org_id.text.strip())

        name = org.find("name")
        self.assertIsNotNone(name)

        name_narrative = name.find("narrative")
        self.assertIsNotNone(name_narrative)
        self.assertTrue(name_narrative.text.strip())

        reporting_org = org.find("reporting-org")
        self.assertIsNotNone(reporting_org)

    def test_xml_namespace_handling(self):
        """Test that XML namespaces are handled correctly."""
        output_path = self.converter.convert_to_xml(self.csv_file, self.xml_file)

        # Read raw XML content to check namespace declarations
        with open(output_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Check that XML namespace declarations are present
        self.assertIn('xmlns:xsd="http://www.w3.org/2001/XMLSchema"', xml_content)
        self.assertIn('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', xml_content)

        # Parse and check xml:lang attribute access
        tree = ET.parse(output_path)
        root = tree.getroot()
        org = root.find("iati-organisation")

        # Test both ways of accessing xml:lang
        xml_lang_1 = org.get("{http://www.w3.org/XML/1998/namespace}lang")
        xml_lang_2 = org.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")

        self.assertEqual(xml_lang_1, "en")
        self.assertEqual(xml_lang_2, "en")

    def _create_test_csv(self, file_path: Path, org_id: str, org_name: str):
        """Helper method to create a test CSV file with basic organisation data."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Organisation Identifier", "Name", "Reporting Org Ref", "Reporting Org Type", "Reporting Org Name"
            ])
            writer.writerow([
                org_id, org_name, org_id, "40", org_name
            ])


if __name__ == "__main__":
    unittest.main()
