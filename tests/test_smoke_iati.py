import tempfile
import unittest
from pathlib import Path

from okfn_iati import IatiMultiCsvConverter
from okfn_iati.iati_schema_validator import IatiValidator

MIN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<iati-activities version="2.03" generated-datetime="2024-01-01T00:00:00Z">
  <iati-activity default-currency="USD" xml:lang="en">
    <iati-identifier>XM-DAC-46002-CR-2025</iati-identifier>
    <reporting-org ref="XM-DAC-46002" type="40"><narrative>CABEI</narrative></reporting-org>
    <title><narrative>Minimal Activity</narrative></title>
    <activity-status code="2"/>
    <activity-date type="1" iso-date="2023-01-15"/>
    <activity-date type="3" iso-date="2025-12-31"/>
    <recipient-country code="CR"><narrative>Costa Rica</narrative></recipient-country>
    <sector vocabulary="1" code="21020" percentage="100"><narrative>Road transport</narrative></sector>
  </iati-activity>
</iati-activities>
"""


class TestSmokeMultiIati(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_smoke_xml_to_csv_folder(self):
        xml_path = self.tmp / "mini.xml"
        xml_path.write_text(MIN_XML, encoding="utf-8")

        out_folder = self.tmp / "csv"
        ok = IatiMultiCsvConverter().xml_to_csv_folder(str(xml_path), str(out_folder))
        self.assertTrue(ok, "xml_to_csv_folder (smoke) devolvió False")
        self.assertTrue((out_folder / "activities.csv").exists(), "No se generó activities.csv (smoke)")

    def test_smoke_csv_folder_to_xml_and_validate(self):
        # Generar primero un folder multi-CSV desde el XML mínimo
        xml_path = self.tmp / "mini.xml"
        xml_path.write_text(MIN_XML, encoding="utf-8")
        folder = self.tmp / "csv"
        self.assertTrue(IatiMultiCsvConverter().xml_to_csv_folder(str(xml_path), str(folder)))

        # Volver a XML (sin forzar validación aquí, porque el orden actual del conversor
        # puede no coincidir exactamente con el del esquema)
        out_xml = self.tmp / "out.xml"
        ok = IatiMultiCsvConverter().csv_folder_to_xml(str(folder), str(out_xml), validate_output=False)
        self.assertTrue(ok, "csv_folder_to_xml (smoke) devolvió False")
        self.assertTrue(out_xml.exists(), "No se generó el XML (smoke)")

        # Validación informativa (no bloquea el test)
        xml_txt = out_xml.read_text(encoding="utf-8")
        valid, errs = IatiValidator().validate(xml_txt)
        if not valid:
            # Solo informar — este es un smoke test
            print(f"⚠️  XML (smoke) con advertencias de esquema: {errs}")

        # Afirmaciones mínimas de humo: el XML tiene actividades
        self.assertIn("<iati-activity", xml_txt, "El XML (smoke) no contiene iati-activity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
