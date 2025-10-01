import csv
import json
import difflib
import tempfile
import unittest
from pathlib import Path

from okfn_iati import IatiCsvConverter, IatiMultiCsvConverter
from okfn_iati.iati_schema_validator import IatiValidator

HERE = Path(__file__).parent.resolve()
SAMPLE_XML = HERE / "test_activities_generated.xml"
SAMPLE_CSV = HERE / "sample_activities.csv"


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


class TestIatiRoundtripSplit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Asegura que existen los fixtures base
        if not SAMPLE_XML.exists():
            raise unittest.SkipTest(f"Missing sample XML at {SAMPLE_XML}")
        if not SAMPLE_CSV.exists():
            raise unittest.SkipTest(f"Missing sample CSV at {SAMPLE_CSV}")

    def setUp(self):
        # temp dir per test to isolate artifacts
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # ---------- 1) XML -> single CSV
    def test_xml_to_single_csv(self):
        out_csv = self.tmp / "from_xml_single.csv"
        IatiCsvConverter().xml_to_csv(str(SAMPLE_XML), str(out_csv))
        assert_file_exists(out_csv)
        with out_csv.open("r", encoding="utf-8") as f:
            rows = sum(1 for _ in f)
        self.assertGreaterEqual(rows, 2, "Expected at least 1 activity row")

    # ---------- 2) XML -> multi-CSV folder
    def test_xml_to_multi_csv_folder(self):
        folder = self.tmp / "from_xml_multi"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(folder))
        self.assertTrue(ok, "xml_to_csv_folder returned False")
        self.assertTrue(folder.exists(), "Multi-CSV folder not created")
        activities_csv = folder / "activities.csv"
        assert_file_exists(activities_csv)
        with activities_csv.open("r", encoding="utf-8") as f:
            rows = sum(1 for _ in f)
        self.assertGreaterEqual(rows, 2, "Expected at least 1 activity row in activities.csv")

    # ---------- 3) CSV (single) -> XML (+ validation)
    def test_csv_single_to_xml_and_validate(self):
        out_xml = self.tmp / "from_csv_single.xml"
        ok = IatiCsvConverter().csv_to_xml(str(SAMPLE_CSV), str(out_xml), validate_output=True)
        self.assertTrue(ok, "csv_to_xml returned False (conversion or validation)")
        assert_file_exists(out_xml)

        with out_xml.open("r", encoding="utf-8") as f:
            xml_string = f.read()
        valid, errs = IatiValidator().validate(xml_string)
        self.assertTrue(valid, f"Generated XML from CSV is invalid:\n{json.dumps(errs, indent=2)}")

    # ---------- 4) Multi-CSV folder -> XML (+ validation)
    def test_csv_folder_to_xml_and_validate(self):
        # first generate the multi-CSV folder
        folder = self.tmp / "from_xml_multi"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(folder))
        self.assertTrue(ok, "xml_to_csv_folder returned False")
        out_xml = self.tmp / "from_multi_xml.xml"
        ok = IatiMultiCsvConverter().csv_folder_to_xml(str(folder), str(out_xml), validate_output=True)
        self.assertTrue(ok, "csv_folder_to_xml returned False (conversion or validation)")
        assert_file_exists(out_xml)

    # ---------- 5) CSV -> XML -> CSV round-trip: compare key fields
    def test_roundtrip_compare_selected_fields(self):
        # CSV -> XML
        mid_xml = self.tmp / "from_csv_single.xml"
        ok = IatiCsvConverter().csv_to_xml(str(SAMPLE_CSV), str(mid_xml), validate_output=True)
        self.assertTrue(ok, "csv_to_xml returned False (conversion or validation)")
        assert_file_exists(mid_xml)

        # XML -> CSV
        roundtrip_csv = self.tmp / "roundtrip.csv"
        IatiCsvConverter().xml_to_csv(str(mid_xml), str(roundtrip_csv))
        assert_file_exists(roundtrip_csv)

        # Key field comparison
        original_row = read_csv_first_row(SAMPLE_CSV)
        recovered_row = read_csv_first_row(roundtrip_csv)
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
            "sector_code",
            "sector_percentage",
        ]
        diffs = compare_selected_fields(original_row, recovered_row, must_match)
        self.assertFalse(
            diffs,
            "Mismatch after CSV -> XML -> CSV round-trip on selected fields:\n"
            + "\n".join(f"  - {k}: '{o}' != '{r}'" for k, o, r in diffs)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
