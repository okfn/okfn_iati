import unittest
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

from okfn_iati.organisation_xml_generator import IatiOrganisationMultiCsvConverter


class TestOrganisationMultiCsvConverter(unittest.TestCase):
    """Test the multi-CSV converter for organisations."""

    def setUp(self):
        """Set up test environment."""
        self.converter = IatiOrganisationMultiCsvConverter()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_xml_path = Path(self.temp_dir.name) / "test_org.xml"
        self.csv_folder_path = Path(self.temp_dir.name) / "csv_output"
        self.regenerated_xml_path = Path(self.temp_dir.name) / "regenerated_org.xml"

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_round_trip_conversion_ares_style(self):
        """Test round-trip conversion for ARES-style organisation with French language."""
        # Create test XML similar to ARES
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<iati-organisations version="2.02" generated-datetime="2018-10-11T14:17:41+00:00">
  <iati-organisation last-updated-datetime="2018-10-11T14:17:41+00:00" xml:lang="fr" default-currency="EUR">
    <organisation-identifier>BE-BCE_KBO-0546740696</organisation-identifier>
    <name>
      <narrative>ARES</narrative>
    </name>
    <reporting-org type="80" ref="BE-BCE_KBO-0546740696">
      <narrative xml:lang="fr">Académie de recherche et d'enseignement supérieur - ARES</narrative>
    </reporting-org>
    <total-budget status="2">
      <period-start iso-date="2017-01-01"/>
      <period-end iso-date="2017-12-31"/>
      <value currency="EUR" value-date="2017-01-01">25354900</value>
    </total-budget>
    <total-budget status="2">
      <period-start iso-date="2018-01-01"/>
      <period-end iso-date="2018-12-31"/>
      <value currency="EUR" value-date="2017-01-01">30253717</value>
    </total-budget>
  </iati-organisation>
</iati-organisations>'''

        # Write test XML to file
        with open(self.test_xml_path, 'w', encoding='utf-8') as f:
            f.write(test_xml)

        # Convert XML to CSV folder
        success = self.converter.xml_to_csv_folder(self.test_xml_path, self.csv_folder_path)
        self.assertTrue(success, "XML to CSV conversion should succeed")

        # Verify CSV files are created
        self.assertTrue((self.csv_folder_path / "organisations.csv").exists())
        self.assertTrue((self.csv_folder_path / "budgets.csv").exists())

        # Convert CSV folder back to XML
        success = self.converter.csv_folder_to_xml(self.csv_folder_path, self.regenerated_xml_path)
        self.assertTrue(success, "CSV to XML conversion should succeed")

        # Parse both XMLs for comparison
        original_tree = ET.parse(self.test_xml_path)
        original_root = original_tree.getroot()

        regenerated_tree = ET.parse(self.regenerated_xml_path)
        regenerated_root = regenerated_tree.getroot()

        # Compare key elements
        original_org = original_root.find('iati-organisation')
        regenerated_org = regenerated_root.find('iati-organisation')

        self.assertIsNotNone(original_org)
        self.assertIsNotNone(regenerated_org)

        # Check xml:lang attribute preservation
        original_lang = original_org.get('{http://www.w3.org/XML/1998/namespace}lang')
        regenerated_lang = regenerated_org.get('{http://www.w3.org/XML/1998/namespace}lang')
        self.assertEqual(original_lang, regenerated_lang, "xml:lang should be preserved")

        # Check default-currency attribute preservation
        original_currency = original_org.get('default-currency')
        regenerated_currency = regenerated_org.get('default-currency')
        self.assertEqual(original_currency, regenerated_currency, "default-currency should be preserved")

        # Check reporting org narrative language
        original_reporting_narrative = original_org.find('reporting-org/narrative')
        regenerated_reporting_narrative = regenerated_org.find('reporting-org/narrative')

        self.assertIsNotNone(original_reporting_narrative)
        self.assertIsNotNone(regenerated_reporting_narrative)

        original_reporting_lang = original_reporting_narrative.get('{http://www.w3.org/XML/1998/namespace}lang')
        regenerated_reporting_lang = regenerated_reporting_narrative.get('{http://www.w3.org/XML/1998/namespace}lang')
        self.assertEqual(
            original_reporting_lang, regenerated_reporting_lang,
            "reporting-org narrative xml:lang should be preserved"
        )

        # Check organisation identifier
        original_id = original_org.find('organisation-identifier').text
        regenerated_id = regenerated_org.find('organisation-identifier').text
        self.assertEqual(original_id, regenerated_id, "Organisation identifier should be preserved")

        # Check budgets count
        original_budgets = original_org.findall('total-budget')
        regenerated_budgets = regenerated_org.findall('total-budget')
        self.assertEqual(
            len(original_budgets), len(regenerated_budgets),
            "Number of budgets should be preserved"
        )

    def test_round_trip_conversion_3fi_style(self):
        """Test round-trip conversion for 3FI-style organisation with Danish currency."""
        # Create test XML similar to 3FI
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<iati-organisations version="2.03" generated-datetime="2025-07-31T09:34:32+00:00">
  <iati-organisation last-updated-datetime="2025-07-31T09:34:32+00:00" xml:lang="en" default-currency="DKK">
    <organisation-identifier>DK-CVR-31378028</organisation-identifier>
    <name>
      <narrative>3F </narrative>
    </name>
    <reporting-org type="22" ref="DK-CVR-31378028">
      <narrative>3F </narrative>
    </reporting-org>
    <total-budget status="2">
      <period-start iso-date="2020-01-01"/>
      <period-end iso-date="2020-12-31"/>
      <value currency="DKK" value-date="2020-01-01">23993333</value>
    </total-budget>
  </iati-organisation>
</iati-organisations>'''

        # Write test XML to file
        with open(self.test_xml_path, 'w', encoding='utf-8') as f:
            f.write(test_xml)

        # Convert XML to CSV folder
        success = self.converter.xml_to_csv_folder(self.test_xml_path, self.csv_folder_path)
        self.assertTrue(success, "XML to CSV conversion should succeed")

        # Convert CSV folder back to XML
        success = self.converter.csv_folder_to_xml(self.csv_folder_path, self.regenerated_xml_path)
        self.assertTrue(success, "CSV to XML conversion should succeed")

        # Parse both XMLs for comparison
        original_tree = ET.parse(self.test_xml_path)
        original_root = original_tree.getroot()

        regenerated_tree = ET.parse(self.regenerated_xml_path)
        regenerated_root = regenerated_tree.getroot()

        # Compare key elements
        original_org = original_root.find('iati-organisation')
        regenerated_org = regenerated_root.find('iati-organisation')

        # Check default currency
        original_currency = original_org.get('default-currency')
        regenerated_currency = regenerated_org.get('default-currency')
        self.assertEqual(
            original_currency, regenerated_currency,
            "DKK default-currency should be preserved"
        )
        self.assertEqual(regenerated_currency, "DKK", "Currency should be DKK")

    def test_complex_organisation_with_expenditures(self):
        """Test organisation with multiple budgets and expenditures."""
        # Create test XML with expenditures
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<iati-organisations version="2.02" generated-datetime="2022-06-30T11:07:47+00:00">
    <iati-organisation last-updated-datetime="2022-05-30T12:14:31+00:00" xml:lang="en" default-currency="EUR">
        <organisation-identifier>BE-BCE_KBO-0420656336</organisation-identifier>
        <name>
            <narrative>Rikolto Belgie VZW</narrative>
        </name>
        <reporting-org type="22" ref="BE-BCE_KBO-0420656336">
            <narrative xml:lang="en">Rikolto België VZW</narrative>
        </reporting-org>
        <total-budget>
            <period-start iso-date="2017-01-01" />
            <period-end iso-date="2017-12-31" />
            <value currency="EUR" value-date="2017-06-30">4572104.00</value>
        </total-budget>
        <total-budget>
            <period-start iso-date="2018-01-01" />
            <period-end iso-date="2018-12-31" />
            <value currency="EUR" value-date="2019-02-21">3378296.00</value>
        </total-budget>
        <total-expenditure>
            <period-start iso-date="2017-01-01" />
            <period-end iso-date="2017-12-31" />
            <value currency="EUR" value-date="2017-03-01">4195574.92</value>
        </total-expenditure>
        <total-expenditure>
            <period-start iso-date="2018-01-01" />
            <period-end iso-date="2018-12-31" />
            <value currency="EUR" value-date="2019-02-21">3282036.00</value>
        </total-expenditure>
    </iati-organisation>
</iati-organisations>'''

        # Write test XML to file
        with open(self.test_xml_path, 'w', encoding='utf-8') as f:
            f.write(test_xml)

        # Convert XML to CSV folder
        success = self.converter.xml_to_csv_folder(self.test_xml_path, self.csv_folder_path)
        self.assertTrue(success)

        # Verify expenditures CSV is created
        self.assertTrue((self.csv_folder_path / "expenditures.csv").exists())

        # Convert back to XML
        success = self.converter.csv_folder_to_xml(self.csv_folder_path, self.regenerated_xml_path)
        self.assertTrue(success)

        # Parse and verify expenditures are preserved
        regenerated_tree = ET.parse(self.regenerated_xml_path)
        regenerated_root = regenerated_tree.getroot()
        regenerated_org = regenerated_root.find('iati-organisation')

        expenditures = regenerated_org.findall('total-expenditure')
        self.assertEqual(len(expenditures), 2, "Should have 2 expenditures")

        # Check expenditure values
        expenditure_values = [exp.find('value').text for exp in expenditures]
        self.assertIn('4195574.92', expenditure_values)
        self.assertIn('3282036.00', expenditure_values)

    def test_template_generation(self):
        """Test CSV template generation."""
        template_folder = Path(self.temp_dir.name) / "templates"

        # Generate templates
        self.converter.generate_csv_templates(template_folder, include_examples=True)

        # Check all template files are created
        expected_files = ["organisations.csv", "budgets.csv", "expenditures.csv", "documents.csv"]
        for filename in expected_files:
            file_path = template_folder / filename
            self.assertTrue(file_path.exists(), f"{filename} should be created")

            # Check file has content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertTrue(len(content) > 0, f"{filename} should not be empty")
                self.assertTrue(
                    "organisation_identifier" in content,
                    f"{filename} should contain organisation_identifier column"
                )


if __name__ == "__main__":
    unittest.main()
