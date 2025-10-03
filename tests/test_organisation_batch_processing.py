import unittest
import tempfile
import csv
from pathlib import Path
import xml.etree.ElementTree as ET

from okfn_iati.organisation_xml_generator import (
    IatiOrganisationCSVConverter,
)


class TestOrganisationBatchProcessing(unittest.TestCase):
    """Test batch processing of multiple organisation files."""

    def setUp(self):
        """Set up test environment."""
        self.converter = IatiOrganisationCSVConverter()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_folder = Path(self.temp_dir.name) / "organisations"
        self.test_folder.mkdir()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_process_multiple_organisations_different_types(self):
        """Test processing organisations with different budget types."""
        # Create organisation with total budget
        self._create_org_csv(
            self.test_folder / "org_total.csv",
            org_id="XM-DAC-100",
            org_name="Total Budget Org",
            budget_kind="total-budget",
            budget_value="5000000"
        )

        # Create organisation with recipient org budget
        self._create_org_csv(
            self.test_folder / "org_recipient.csv",
            org_id="XM-DAC-200",
            org_name="Recipient Org Budget",
            budget_kind="recipient-org-budget",
            budget_value="2000000",
            recipient_org_ref="XM-DAC-999",
            recipient_org_name="Recipient Organization"
        )

        # Create organisation with country budget
        self._create_org_csv(
            self.test_folder / "org_country.csv",
            org_id="XM-DAC-300",
            org_name="Country Budget Org",
            budget_kind="recipient-country-budget",
            budget_value="3000000",
            recipient_country_code="CR"
        )

        # Process all files
        records = self.converter.read_multiple_from_folder(self.test_folder)

        # Validate records
        self.assertEqual(len(records), 3)

        # Check budget types
        org_ids = {record.org_identifier: record for record in records}

        # Total budget org
        total_org = org_ids["XM-DAC-100"]
        self.assertEqual(len(total_org.budgets), 1)
        self.assertEqual(total_org.budgets[0].kind, "total-budget")
        self.assertEqual(total_org.budgets[0].value, "5000000")

        # Recipient org budget
        recipient_org = org_ids["XM-DAC-200"]
        self.assertEqual(len(recipient_org.budgets), 1)
        self.assertEqual(recipient_org.budgets[0].kind, "recipient-org-budget")
        self.assertEqual(recipient_org.budgets[0].recipient_org_ref, "XM-DAC-999")

        # Country budget org
        country_org = org_ids["XM-DAC-300"]
        self.assertEqual(len(country_org.budgets), 1)
        self.assertEqual(country_org.budgets[0].kind, "recipient-country-budget")
        self.assertEqual(country_org.budgets[0].recipient_country_code, "CR")

    def test_generate_xml_with_multiple_budget_types(self):
        """Test XML generation with different budget types."""
        # Create test files
        self._create_org_csv(
            self.test_folder / "org1.csv",
            org_id="XM-DAC-400",
            org_name="Multi Budget Org",
            budget_kind="total-budget",
            budget_value="1000000"
        )

        self._create_org_csv(
            self.test_folder / "org2.csv",
            org_id="XM-DAC-500",
            org_name="Region Budget Org",
            budget_kind="recipient-region-budget",
            budget_value="800000",
            recipient_region_code="289",
            recipient_region_vocabulary="1"
        )

        # Convert to XML
        xml_output = self.test_folder / "output.xml"
        output_path = self.converter.convert_folder_to_xml(self.test_folder, xml_output)

        # Parse and validate XML
        tree = ET.parse(output_path)
        root = tree.getroot()

        organisations = root.findall("iati-organisation")
        self.assertEqual(len(organisations), 2)

        # Check total budget organisation
        org1 = None
        org2 = None
        for org in organisations:
            org_id = org.find("organisation-identifier").text
            if org_id == "XM-DAC-400":
                org1 = org
            elif org_id == "XM-DAC-500":
                org2 = org

        self.assertIsNotNone(org1)
        self.assertIsNotNone(org2)

        # Check total budget
        total_budget = org1.find("total-budget")
        self.assertIsNotNone(total_budget)

        # Check recipient region budget
        region_budget = org2.find("recipient-region-budget")
        self.assertIsNotNone(region_budget)

        region_elem = region_budget.find("recipient-region")
        self.assertIsNotNone(region_elem)
        self.assertEqual(region_elem.get("code"), "289")
        self.assertEqual(region_elem.get("vocabulary"), "1")

    def test_large_batch_processing(self):
        """Test processing a larger number of organisation files."""
        num_orgs = 50

        # Create many organisation files
        for i in range(num_orgs):
            org_file = self.test_folder / f"org_{i:03d}.csv"
            self._create_org_csv(
                org_file,
                org_id=f"XM-DAC-{1000 + i}",
                org_name=f"Organisation {i:03d}",
                budget_kind="total-budget",
                budget_value=str((i + 1) * 100000)
            )

        # Process all files
        records = self.converter.read_multiple_from_folder(self.test_folder)

        self.assertEqual(len(records), num_orgs)

        # Verify no duplicates
        identifiers = [record.org_identifier for record in records]
        self.assertEqual(len(identifiers), len(set(identifiers)))

        # Convert to XML and verify structure
        xml_output = self.test_folder / "large_batch.xml"
        output_path = self.converter.convert_folder_to_xml(self.test_folder, xml_output)

        tree = ET.parse(output_path)
        root = tree.getroot()

        organisations = root.findall("iati-organisation")
        self.assertEqual(len(organisations), num_orgs)

    def test_error_handling_invalid_files(self):
        """Test error handling when some files are invalid."""
        # Create valid file
        self._create_org_csv(
            self.test_folder / "valid_org.csv",
            org_id="XM-DAC-VALID",
            org_name="Valid Organisation"
        )

        # Create invalid file (missing required fields)
        invalid_file = self.test_folder / "invalid_org.csv"
        with open(invalid_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Wrong", "Headers"])
            writer.writerow(["Invalid", "Data"])

        # Create empty file
        empty_file = self.test_folder / "empty_org.csv"
        with open(empty_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Organisation Identifier", "Name"])
            # No data rows

        # Process folder - should succeed with valid file, log errors for invalid ones
        records = self.converter.read_multiple_from_folder(self.test_folder)

        # Should have processed only the valid file
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].org_identifier, "XM-DAC-VALID")

    def test_validation_across_multiple_files(self):
        """Test validation of organisation identifiers across multiple files."""
        # Create files with duplicate organisation identifiers
        self._create_org_csv(
            self.test_folder / "org1.csv",
            org_id="XM-DAC-DUPLICATE",
            org_name="First Organisation"
        )

        self._create_org_csv(
            self.test_folder / "org2.csv",
            org_id="XM-DAC-UNIQUE",
            org_name="Unique Organisation"
        )

        self._create_org_csv(
            self.test_folder / "org3.csv",
            org_id="XM-DAC-DUPLICATE",  # Duplicate identifier
            org_name="Duplicate Organisation"
        )

        # Read all records
        records = self.converter.read_multiple_from_folder(self.test_folder)

        # Validate for duplicates
        duplicates = self.converter.validate_organisation_identifiers(records)

        self.assertEqual(len(duplicates), 1)
        self.assertIn("XM-DAC-DUPLICATE", duplicates)

    def _create_org_csv(
            self, file_path: Path, org_id: str, org_name: str,
            budget_kind: str = None, budget_value: str = None,
            recipient_org_ref: str = None, recipient_org_name: str = None,
            recipient_country_code: str = None, recipient_region_code: str = None,
            recipient_region_vocabulary: str = None
    ):
        """Helper method to create organisation CSV files with various configurations."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Headers
            headers = [
                "Organisation Identifier", "Name", "Reporting Org Ref", "Reporting Org Type", "Reporting Org Name"
            ]

            if budget_kind:
                headers.extend([
                    "Budget Kind", "Budget Status", "Budget Period Start", "Budget Period End",
                    "Budget Value", "Currency"
                ])

                if recipient_org_ref:
                    headers.extend(["Recipient Org Ref", "Recipient Org Name"])

                if recipient_country_code:
                    headers.append("Recipient Country Code")

                if recipient_region_code:
                    headers.extend(["Recipient Region Code", "Recipient Region Vocabulary"])

            writer.writerow(headers)

            # Data row
            row_data = [org_id, org_name, org_id, "40", org_name]

            if budget_kind:
                row_data.extend([
                    budget_kind, "2", "2023-01-01", "2023-12-31",
                    budget_value or "1000000", "USD"
                ])

                if recipient_org_ref:
                    row_data.extend([recipient_org_ref, recipient_org_name or ""])

                if recipient_country_code:
                    row_data.append(recipient_country_code)

                if recipient_region_code:
                    row_data.extend([recipient_region_code, recipient_region_vocabulary or "1"])

            writer.writerow(row_data)


if __name__ == "__main__":
    unittest.main()
