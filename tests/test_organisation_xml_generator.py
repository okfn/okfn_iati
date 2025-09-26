import unittest
import tempfile
from pathlib import Path

from okfn_iati.organisation_xml_generator import (
    IatiOrganisationCSVConverter,
    IatiOrganisationXMLGenerator,
)

class TestOrganisationXMLGenerator(unittest.TestCase):
    def setUp(self):
        """Create a temporary CSV file for testing."""
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

if __name__ == "__main__":
    unittest.main()
