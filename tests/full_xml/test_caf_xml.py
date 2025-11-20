import os
import unittest
import tempfile
from pathlib import Path
from okfn_iati.multi_csv_converter import IatiMultiCsvConverter
from okfn_iati.xml_comparator import IatiXmlComparator


class TestCafXML(unittest.TestCase):
    """Test parsing and generation of CAF XML data."""

    def setUp(self):
        self.data_dir = os.path.join(
            Path(__file__).parent.parent.parent,
            'data-samples', 'xml'
        )
        self.caf_xml_path = os.path.join(self.data_dir, 'CAF-ActivityFile-2025-10-10.xml')
        
        self.converter = IatiMultiCsvConverter()
        self.comparator = IatiXmlComparator(
            ignore_element_order=True,
            ignore_whitespace=True,
            ignore_empty_attributes=True
        )

        # Paths to test files
        self.original_xml = Path(self.caf_xml_path)

    def test_xml_roundtrip_conversion(self):
        """Test that XML -> CSV -> XML roundtrip preserves data."""
        if not self.original_xml.exists():
            self.skipTest(f"CAF XML file not found: {self.original_xml}")

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_folder = Path(tmpdir) / "csv"
            output_xml = Path(tmpdir) / "output.xml"

            # Convert XML to CSV
            success = self.converter.xml_to_csv_folder(
                self.original_xml,
                csv_folder,
                overwrite=True
            )
            self.assertTrue(success, "XML to CSV conversion failed")

            # Convert CSV back to XML
            success = self.converter.csv_folder_to_xml(
                csv_folder,
                output_xml,
                validate_output=False
            )
            self.assertTrue(success, "CSV to XML conversion failed")

            # Compare original and converted XML
            are_equivalent, differences = self.comparator.compare_files(
                str(self.original_xml),
                str(output_xml)
            )

            # Print differences if any
            if not are_equivalent:
                print("\n" + "="*80)
                print("XML COMPARISON DIFFERENCES:")
                print("="*80)
                print(self.comparator.format_differences(differences, show_non_relevant=False))
                print("="*80)

                # Save both files outside this temp dir for the user to analyze them
                saved_dir = Path.cwd() / "xml_comparison_output"
                saved_dir.mkdir(exist_ok=True)
                saved_original = saved_dir / "original_caf.xml"
                saved_converted = saved_dir / "converted_caf.xml"
                
                # Read and write bytes to avoid encoding issues
                saved_original.write_bytes(self.original_xml.read_bytes())
                saved_converted.write_bytes(output_xml.read_bytes())
                
                print(f"Saved original XML to: {saved_original}")
                print(f"Saved converted XML to: {saved_converted}")

            # Assert files are equivalent
            self.assertTrue(
                are_equivalent,
                "Roundtrip conversion produced differences. See output above."
            )

if __name__ == "__main__":
    unittest.main()
