# tests/test_smoke_iati.py
import csv
from pathlib import Path
import tempfile
import unittest
from okfn_iati import IatiCsvConverter

MIN_HEADERS = [
    "activity_identifier",
    "title",
    "description",
    "activity_status",
    "default_currency",
    "reporting_org_ref",
    "reporting_org_name",
    "reporting_org_type",
    "recipient_country_code",
    "sector_code",
    "sector_percentage",
    "planned_start_date",
    "planned_end_date",
]


class TestSmokeIati(unittest.TestCase):
    def test_smoke_csv_to_xml_minimal(self):
        """Prueba de humo: CSV mínimo a XML"""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            csv_path = td / "mini.csv"
            xml_path = td / "out.xml"

            row = {
                "activity_identifier": "XM-DAC-46002-CR-2025",
                "title": "Minimal Activity",
                "description": "Just enough fields",
                "activity_status": "2",
                "default_currency": "USD",
                "reporting_org_ref": "XM-DAC-46002",
                "reporting_org_name": "CABEI",
                "reporting_org_type": "40",
                "recipient_country_code": "CR",
                "sector_code": "21020",
                "sector_percentage": "100",
                "planned_start_date": "2023-01-15",
                "planned_end_date": "2025-12-31",
            }

            with csv_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=MIN_HEADERS)
                w.writeheader()
                w.writerow(row)

            ok = IatiCsvConverter().csv_to_xml(str(csv_path), str(xml_path), validate_output=False)
            self.assertTrue(ok, "csv_to_xml (smoke) devolvió False")
            self.assertTrue(xml_path.exists(), "No se generó el XML")
            xml_text = xml_path.read_text(encoding="utf-8")
            self.assertIn("<iati-activity", xml_text, "El XML no contiene ninguna iati-activity (smoke)")

    def test_smoke_xml_to_csv_minimal(self):
        """Prueba de humo: XML mínimo a CSV"""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            xml_path = td / "mini.xml"
            csv_path = td / "out.csv"

            xml_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<iati-activities version="2.03" generated-datetime="2024-01-01T00:00:00Z">
  <iati-activity default-currency="USD">
    <iati-identifier>XM-DAC-46002-CR-2025</iati-identifier>
    <reporting-org ref="XM-DAC-46002" type="40">
      <narrative>CABEI</narrative>
    </reporting-org>
    <title><narrative>Minimal Activity</narrative></title>
    <activity-status code="2"/>
    <recipient-country code="CR"><narrative>Costa Rica</narrative></recipient-country>
    <sector vocabulary="1" code="21020" percentage="100"><narrative>Road transport</narrative></sector>
  </iati-activity>
</iati-activities>
                """,
                encoding="utf-8",
            )

            IatiCsvConverter().xml_to_csv(str(xml_path), str(csv_path))
            self.assertTrue(csv_path.exists(), "No se generó el CSV")
            with csv_path.open("r", encoding="utf-8") as f:
                self.assertGreaterEqual(sum(1 for _ in f), 2, "CSV sin filas (smoke)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
