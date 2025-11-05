import csv
import json
import difflib
import tempfile
import unittest
from pathlib import Path

from okfn_iati import IatiMultiCsvConverter
from okfn_iati.iati_schema_validator import IatiValidator

HERE = Path(__file__).parent.resolve()
SAMPLE_XML = HERE / "test_activities_generated.xml"


def assert_file_exists(p: Path):
    if not p.exists():
        raise AssertionError(f"Expected file not found: {p}")


def read_csv_first_row(p: Path):
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row
    return {}


def compare_selected_fields(original: dict, recovered: dict, fields: list):
    diffs = []
    for k in fields:
        o = (original.get(k) or "").strip()
        r = (recovered.get(k) or "").strip()
        if o != r:
            diffs.append((k, o, r))
    return diffs


def pretty_diff(text_a: str, text_b: str, fromfile="original", tofile="generated"):
    return "".join(difflib.unified_diff(
        text_a.splitlines(keepends=True),
        text_b.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile
    ))


class TestIatiMultiRoundtrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure base fixtures exist
        if not SAMPLE_XML.exists():
            raise unittest.SkipTest(f"Missing sample XML at {SAMPLE_XML}")

    def setUp(self):
        # temp dir per test to isolate artifacts
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # 1) XML -> multi-CSV folder
    def test_xml_to_multi_csv_folder(self):
        """Convert sample XML to multi-CSV folder."""
        folder = self.tmp / "from_xml_multi"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(folder))
        self.assertTrue(ok, "xml_to_csv_folder returned False")
        self.assertTrue(folder.exists(), "Multi-CSV folder not created")
        activities_csv = folder / "activities.csv"
        assert_file_exists(activities_csv)
        with activities_csv.open("r", encoding="utf-8") as f:
            rows = sum(1 for _ in f)
        self.assertGreaterEqual(rows, 2, "Expected at least 1 activity row in activities.csv")

    # 2) Multi-CSV folder -> XML (+ validation)
    def test_csv_folder_to_xml_and_validate(self):
        """Convert multi-CSV folder back to XML and validate."""
        # First: generate multi-CSV folder from sample XML
        folder = self.tmp / "from_xml_multi"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(folder))
        self.assertTrue(ok, "xml_to_csv_folder returned False")

        out_xml = self.tmp / "from_multi_xml.xml"
        ok = IatiMultiCsvConverter().csv_folder_to_xml(str(folder), str(out_xml), validate_output=True)
        self.assertTrue(ok, "csv_folder_to_xml returned False (conversion or validation)")
        assert_file_exists(out_xml)

        # Additional direct validation (belt & suspenders)
        xml_text = out_xml.read_text(encoding="utf-8")
        valid, errs = IatiValidator().validate(xml_text)
        self.assertTrue(valid, f"Generated XML from multi-CSV is invalid:\n{json.dumps(errs, indent=2)}")

    # 3) Round-trip: XML -> CSV folder -> XML -> CSV folder (compare key fields in activities.csv)
    def test_roundtrip_compare_selected_fields_from_activities(self):
        """Round-trip multi-CSV conversion and compare selected fields in activities.csv."""
        # Step A: XML -> folder A
        folder_a = self.tmp / "csv_a"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(folder_a))
        self.assertTrue(ok, "xml_to_csv_folder (A) returned False")
        act_a = folder_a / "activities.csv"
        assert_file_exists(act_a)
        original_row = read_csv_first_row(act_a)

        # Step B: folder A -> intermediate XML
        mid_xml = self.tmp / "mid.xml"
        ok = IatiMultiCsvConverter().csv_folder_to_xml(str(folder_a), str(mid_xml), validate_output=True)
        self.assertTrue(ok, "csv_folder_to_xml returned False")
        assert_file_exists(mid_xml)

        # Step C: intermediate XML -> folder B
        folder_b = self.tmp / "csv_b"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(mid_xml), str(folder_b))
        self.assertTrue(ok, "xml_to_csv_folder (B) returned False")
        act_b = folder_b / "activities.csv"
        assert_file_exists(act_b)
        recovered_row = read_csv_first_row(act_b)

        # Fields that should remain stable in activities.csv
        must_match = [
            "activity_identifier",
            "title",
            "description",
            "activity_status",
            "default_currency",
            "reporting_org_ref",
            "reporting_org_name",
            "reporting_org_type",
            "planned_start_date",
            "planned_end_date",
            "recipient_country_code",
        ]
        diffs = compare_selected_fields(original_row, recovered_row, must_match)
        self.assertFalse(
            diffs,
            "Mismatch after multi-CSV round-trip on selected fields:\n"
            + "\n".join(f"  - {k}: '{o}' != '{r}'" for k, o, r in diffs)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
