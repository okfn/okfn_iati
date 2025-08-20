
import csv
import json
import sys
import difflib
import tempfile
from pathlib import Path

# --- Optional: make local package importable if running inside a repo checkout ---
# If you have the sources locally (e.g., okfn_iati folder), uncomment to prioritize local code:
# repo_src = Path(__file__).parent / "src"
# if repo_src.exists():
#     sys.path.insert(0, str(repo_src))

# Primary imports (from installed package)
from okfn_iati import IatiCsvConverter, IatiMultiCsvConverter
from okfn_iati.iati_schema_validator import IatiValidator

HERE = Path(__file__).parent.resolve()

SAMPLE_XML = HERE / "sample.xml"
SAMPLE_CSV = HERE / "sample_activities.csv"


def assert_file_exists(p: Path):
    assert p.exists(), f"Expected file not found: {p}"


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


def test_roundtrip_end_to_end():
    '''
    End-to-end tests covering:
      1) XML -> single CSV
      2) XML -> multi-CSV folder
      3) CSV (single) -> XML (+ validation)
      4) Multi-CSV folder -> XML (+ validation)
      5) CSV -> XML -> CSV round-trip: compare key fields
    '''
    assert SAMPLE_XML.exists(), f"Missing sample XML at {SAMPLE_XML}"
    assert SAMPLE_CSV.exists(), f"Missing sample CSV at {SAMPLE_CSV}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # ---------- 1) XML -> single CSV
        xml_to_csv_out = tmp / "from_xml_single.csv"
        IatiCsvConverter().xml_to_csv(str(SAMPLE_XML), str(xml_to_csv_out))
        assert_file_exists(xml_to_csv_out)
        # At least header + 1 row
        with xml_to_csv_out.open("r", encoding="utf-8") as f:
            rows = sum(1 for _ in f)
        assert rows >= 2, f"Expected at least 1 activity row in {xml_to_csv_out}"

        # ---------- 2) XML -> multi-CSV folder
        multi_folder = tmp / "from_xml_multi"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(SAMPLE_XML), str(multi_folder))
        assert ok, "xml_to_csv_folder returned False"
        assert multi_folder.exists(), "Multi-CSV folder not created"
        # activities.csv must exist and have ≥1 row
        activities_csv = multi_folder / "activities.csv"
        assert_file_exists(activities_csv)
        with activities_csv.open("r", encoding="utf-8") as f:
            rows = sum(1 for _ in f)
        assert rows >= 2, "Expected at least 1 activity row in activities.csv"

        # ---------- 3) CSV (single) -> XML (+ validation)
        csv_to_xml_out = tmp / "from_csv_single.xml"
        ok = IatiCsvConverter().csv_to_xml(str(SAMPLE_CSV), str(csv_to_xml_out), validate_output=True)
        assert ok, "csv_to_xml returned False (conversion or validation)"
        assert_file_exists(csv_to_xml_out)
        # Extra: validate again explicitly
        with csv_to_xml_out.open("r", encoding="utf-8") as f:
            xml_string = f.read()
        valid, errs = IatiValidator().validate(xml_string)
        assert valid, f"Generated XML from CSV is invalid:\\n{json.dumps(errs, indent=2)}"

        # ---------- 4) Multi-CSV folder -> XML (+ validation)
        multi_to_xml_out = tmp / "from_multi_xml.xml"
        ok = IatiMultiCsvConverter().csv_folder_to_xml(str(multi_folder), str(multi_to_xml_out), validate_output=True)
        assert ok, "csv_folder_to_xml returned False (conversion or validation)"
        assert_file_exists(multi_to_xml_out)

        # ---------- 5) CSV -> XML -> CSV round-trip comparisons
        roundtrip_csv = tmp / "roundtrip.csv"
        IatiCsvConverter().xml_to_csv(str(csv_to_xml_out), str(roundtrip_csv))
        assert_file_exists(roundtrip_csv)

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
            # keep the set small—some fields may expand/normalize across conversions
        ]

        diffs = compare_selected_fields(original_row, recovered_row, must_match)
        assert not diffs, (
            "Mismatch after CSV -> XML -> CSV round-trip on selected fields:\\n"
            + "\\n".join(f"  - {k}: '{o}' != '{r}'" for k, o, r in diffs)
        )

        # Optional: print sample of produced files for debugging
        print(f"\\nArtifacts in {tmp}:")
        for p in sorted(tmp.rglob("*")):
            if p.is_file():
                print(" -", p.relative_to(tmp))


if __name__ == '__main__':
    # Allow running as a simple script without pytest
    try:
        test_roundtrip_end_to_end()
        print("\\n✅ All end-to-end tests passed.")
    except AssertionError as e:
        print("\\n❌ Test failed:")
        print(e)
        sys.exit(1)
