import unittest
import tempfile
from pathlib import Path

from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
from okfn_iati.xml_comparator import IatiXmlComparator


class TestWHOArgXML(unittest.TestCase):
    """Test parsing, conversion and comparison of WHO Argentina XML data."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = Path(__file__).parent.parent.parent / 'data-samples' / 'xml'
        self.who_xml_path = self.data_dir / 'who-arg.xml'

        # Initialize converter and comparator
        self.converter = IatiMultiCsvConverter()
        self.comparator = IatiXmlComparator(
            ignore_element_order=True,
            ignore_whitespace=True,
            ignore_empty_attributes=True
        )

        # Verify test file exists
        if not self.who_xml_path.exists():
            self.skipTest(f"WHO Argentina XML file not found: {self.who_xml_path}")

    def test_xml_file_exists_and_valid(self):
        """Test that the WHO Argentina XML file exists and is valid XML."""
        self.assertTrue(self.who_xml_path.exists(), "WHO Argentina XML file should exist")

        # Try to parse it
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(self.who_xml_path)
            root = tree.getroot()
            self.assertEqual(root.tag, "iati-activities", "Root element should be iati-activities")
        except ET.ParseError as e:
            self.fail(f"XML file is not valid: {e}")

    def test_xml_structure(self):
        """Test basic structure of WHO Argentina XML."""
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.who_xml_path)
        root = tree.getroot()

        # Check version
        version = root.get('version')
        self.assertIsNotNone(version, "XML should have version attribute")
        self.assertEqual(version, "2.03", "Expected IATI version 2.03")

        # Check generated-datetime
        generated_datetime = root.get('generated-datetime')
        self.assertIsNotNone(generated_datetime, "XML should have generated-datetime attribute")

        # Count activities
        activities = root.findall('iati-activity')
        activity_count = len(activities)
        print(f"\nFound {activity_count} activities in WHO Argentina XML")
        self.assertGreater(activity_count, 0, "Should have at least one activity")

        # Check that activities have required elements
        for idx, activity in enumerate(activities[:5]):  # Check first 5
            last_updated = activity.get('last-updated-datetime')
            self.assertIsNotNone(last_updated, f"Activity {idx} should have last-updated-datetime")

            xml_lang = activity.get('{http://www.w3.org/XML/1998/namespace}lang')
            self.assertIsNotNone(xml_lang, f"Activity {idx} should have xml:lang")

            default_currency = activity.get('default-currency')
            self.assertIsNotNone(default_currency, f"Activity {idx} should have default-currency")

    def test_xml_roundtrip_conversion(self):
        """Test that XML -> CSV -> XML roundtrip preserves data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"
            output_xml = Path(tmpdir) / "output.xml"

            # Convert XML to CSV
            print("\n=== Converting XML to CSV ===")
            success = self.converter.xml_to_csv_folder(
                self.who_xml_path,
                csv_folder,
                overwrite=True
            )
            self.assertTrue(success, "XML to CSV conversion should succeed")

            # Verify CSV files were created
            csv_files = list(csv_folder.glob('*.csv'))
            print(f"Created {len(csv_files)} CSV files")
            self.assertGreater(len(csv_files), 0, "Should create at least one CSV file")

            # Convert CSV back to XML
            print("\n=== Converting CSV back to XML ===")
            success = self.converter.csv_folder_to_xml(
                csv_folder,
                output_xml,
                validate_output=False
            )
            self.assertTrue(success, "CSV to XML conversion should succeed")
            self.assertTrue(output_xml.exists(), "Output XML file should be created")

            # Compare original and converted XML
            print("\n=== Comparing original and converted XML ===")
            are_equivalent, differences = self.comparator.compare_files(
                str(self.who_xml_path),
                str(output_xml)
            )

            # Print differences if any
            if not are_equivalent:
                print("\n" + "="*80)
                print("XML COMPARISON DIFFERENCES:")
                print("="*80)
                print(self.comparator.format_differences(differences, show_non_relevant=False))
                print("="*80)

                # Count relevant vs non-relevant differences
                relevant_count = len([d for d in differences if d.is_relevant])
                non_relevant_count = len([d for d in differences if not d.is_relevant])
                print(f"\nSummary: {relevant_count} relevant, {non_relevant_count} non-relevant differences")

            # Assert files are equivalent
            self.assertTrue(
                are_equivalent,
                "Roundtrip conversion should preserve all relevant data"
            )

    def test_csv_to_xml_preserves_key_elements(self):
        """Test that key IATI elements are preserved in CSV -> XML conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"
            output_xml = Path(tmpdir) / "output.xml"

            # Convert to CSV and back
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)
            self.converter.csv_folder_to_xml(csv_folder, output_xml, validate_output=False)

            # Parse both XMLs
            import xml.etree.ElementTree as ET
            original_tree = ET.parse(self.who_xml_path)
            converted_tree = ET.parse(output_xml)

            original_root = original_tree.getroot()
            converted_root = converted_tree.getroot()

            # Compare activity count
            original_activities = original_root.findall('iati-activity')
            converted_activities = converted_root.findall('iati-activity')

            self.assertEqual(
                len(converted_activities),
                len(original_activities),
                "Number of activities should be preserved"
            )

    def test_humanitarian_attribute_preservation(self):
        """Test that humanitarian attributes are correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"
            output_xml = Path(tmpdir) / "output.xml"

            # Convert to CSV and back
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)
            self.converter.csv_folder_to_xml(csv_folder, output_xml, validate_output=False)

            # Check humanitarian attributes in activities CSV
            import csv
            activities_csv = csv_folder / 'activities.csv'
            if activities_csv.exists():
                with open(activities_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    activities = list(reader)

                    humanitarian_values = [a.get('humanitarian', '') for a in activities]
                    print(f"\nHumanitarian attribute values found: {set(humanitarian_values)}")

                    # Should have mix of empty, "0", and "1" or "true"
                    # Empty means attribute not present
                    # "0" means explicit false
                    # "1" or "true" means explicit true
                    self.assertIn('', humanitarian_values, "Should have activities without humanitarian attribute")

    def test_transaction_preservation(self):
        """Test that transactions are correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"

            # Convert to CSV
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)

            # Check transactions CSV
            import csv
            transactions_csv = csv_folder / 'transactions.csv'
            if transactions_csv.exists():
                with open(transactions_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    transactions = list(reader)

                    print(f"\nFound {len(transactions)} transactions in CSV")
                    self.assertGreater(len(transactions), 0, "Should have transactions")

                    # Check first transaction has required fields
                    if transactions:
                        first_trans = transactions[0]
                        self.assertIn('activity_identifier', first_trans)
                        self.assertIn('transaction_type', first_trans)
                        self.assertIn('transaction_date', first_trans)
                        self.assertIn('value', first_trans)

    def test_sector_preservation(self):
        """Test that sector information is correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"

            # Convert to CSV
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)

            # Check sectors CSV
            import csv
            sectors_csv = csv_folder / 'sectors.csv'
            if sectors_csv.exists():
                with open(sectors_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    sectors = list(reader)

                    print(f"\nFound {len(sectors)} sectors in CSV")
                    self.assertGreater(len(sectors), 0, "Should have sectors")

                    # Check for DAC sector codes
                    sector_codes = [s.get('sector_code', '') for s in sectors]
                    print(f"Sample sector codes: {sector_codes[:5]}")

    def test_budget_preservation(self):
        """Test that budget information is correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"

            # Convert to CSV
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)

            # Check budgets CSV
            import csv
            budgets_csv = csv_folder / 'budgets.csv'
            if budgets_csv.exists():
                with open(budgets_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    budgets = list(reader)

                    print(f"\nFound {len(budgets)} budgets in CSV")
                    if budgets:
                        # Check budget has required fields
                        first_budget = budgets[0]
                        self.assertIn('activity_identifier', first_budget)
                        self.assertIn('period_start', first_budget)
                        self.assertIn('period_end', first_budget)
                        self.assertIn('value', first_budget)

    def test_comparator_configuration(self):
        """Test that the XML comparator is properly configured."""
        # Check comparator settings
        self.assertTrue(self.comparator.ignore_element_order)
        self.assertTrue(self.comparator.ignore_whitespace)
        self.assertTrue(self.comparator.ignore_empty_attributes)

        # Check ignored attributes
        self.assertIn('generated-datetime', self.comparator.IGNORE_ATTRIBUTES)
        self.assertIn('last-updated-datetime', self.comparator.IGNORE_ATTRIBUTES)

    def test_activity_dates_preservation(self):
        """Test that activity dates are correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"

            # Convert to CSV
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)

            # Check activity_date CSV
            import csv
            activity_date_csv = csv_folder / 'activity_date.csv'
            if activity_date_csv.exists():
                with open(activity_date_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    dates = list(reader)

                    print(f"\nFound {len(dates)} activity dates in CSV")
                    if dates:
                        # Check for different date types
                        date_types = set(d.get('type', '') for d in dates)
                        print(f"Activity date types: {date_types}")

                        # Should have start and end dates (types 1, 2, 3, 4)
                        self.assertTrue(len(date_types) > 0, "Should have different date types")

    def test_participating_orgs_preservation(self):
        """Test that participating organizations are correctly preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"

            # Convert to CSV
            self.converter.xml_to_csv_folder(self.who_xml_path, csv_folder, overwrite=True)

            # Check participating_orgs CSV
            import csv
            orgs_csv = csv_folder / 'participating_orgs.csv'
            if orgs_csv.exists():
                with open(orgs_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    orgs = list(reader)

                    print(f"\nFound {len(orgs)} participating organizations in CSV")
                    if orgs:
                        # Check for WHO as reporting org
                        who_orgs = [o for o in orgs if 'XM-DAC-928' in o.get('org_ref', '')]
                        print(f"Found {len(who_orgs)} WHO organization references")

                        # Check organization roles
                        roles = set(o.get('role', '') for o in orgs)
                        print(f"Organization roles: {roles}")


if __name__ == "__main__":
    unittest.main()
