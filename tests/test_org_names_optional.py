import csv
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from okfn_iati.organisation_xml_generator import IatiOrganisationCSVConverter, IatiOrganisationMultiCsvConverter


class TestOrganisationNamesOptional(unittest.TestCase):
    def setUp(self):
        self.tmpctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmpctx.name)

    def tearDown(self):
        self.tmpctx.cleanup()

    def test_csv_to_xml_without_names_csv(self):
        """If there is no names.csv, use the main name (single narrative without xml:lang)."""
        folder = self.tmp / "csv_in"
        folder.mkdir()
        org_csv = folder / "organisations.csv"
        with org_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "Organisation Identifier", "Name", "Reporting Org Ref",
                "Reporting Org Type", "Reporting Org Name", "Default Currency", "xml_lang"
            ])
            w.writerow([
                "ORG-123", "Mi Organización", "ORG-123", "40", "Mi Organización", "USD", "es"
            ])

        out_xml = self.tmp / "out.xml"
        conv = IatiOrganisationCSVConverter()
        # Convert CSV to XML
        result = conv.convert_folder_to_xml(folder, out_xml)
        self.assertEqual(str(out_xml), result)
        self.assertTrue(out_xml.exists(), "No se generó el XML de salida")

        # Validate: single narrative without xml:lang; xml:lang in iati-organisation = "es"
        root = ET.parse(out_xml).getroot()
        org = root.find("iati-organisation")
        self.assertIsNotNone(org)
        self.assertEqual(org.get("{http://www.w3.org/XML/1998/namespace}lang"), "es")

        name = org.find("name")
        self.assertIsNotNone(name)
        narratives = name.findall("narrative")
        self.assertEqual(len(narratives), 1)
        self.assertEqual(narratives[0].text, "Mi Organización")
        self.assertIsNone(narratives[0].get("{http://www.w3.org/XML/1998/namespace}lang"))

    def test_xml_to_csv_with_single_name_does_not_create_names_csv(self):
        """XML with a single <narrative>: names.csv should NOT be generated."""
        in_xml = self.tmp / "one_name.xml"
        in_xml.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
            <iati-organisations version="2.03">
            <iati-organisation xml:lang="es" default-currency="USD">
                <organisation-identifier>ORG-123</organisation-identifier>
                <name><narrative>Mi Organización</narrative></name>
                <reporting-org ref="ORG-123" type="40"><narrative>Mi Organización</narrative></reporting-org>
            </iati-organisation>
            </iati-organisations>""",
            encoding="utf-8",
        )

        out_folder = self.tmp / "csv_out"
        multi = IatiOrganisationMultiCsvConverter()
        ok = multi.xml_to_csv_folder(in_xml, out_folder)
        self.assertTrue(ok, "xml_to_csv_folder devolvió False")
        self.assertTrue((out_folder / "organisations.csv").exists(), "Falta organisations.csv")
        self.assertFalse((out_folder / "names.csv").exists(), "names.csv no debería existir con un solo nombre")

    def test_xml_to_csv_with_multiple_names_creates_names_csv(self):
        """XML with multiple <narrative>: MUST create names.csv with rows per language."""
        in_xml = self.tmp / "multi_name.xml"
        in_xml.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
                <iati-organisations version="2.03">
                <iati-organisation xml:lang="es" default-currency="USD">
                    <organisation-identifier>ORG-123</organisation-identifier>
                    <name>
                    <narrative>Mi Organización</narrative>
                    <narrative xml:lang="en">My Organisation</narrative>
                    <narrative xml:lang="fr">Mon Organisation</narrative>
                    </name>
                    <reporting-org ref="ORG-123" type="40"><narrative>Mi Organización</narrative></reporting-org>
                </iati-organisation>
                </iati-organisations>""",
            encoding="utf-8",
        )

        out_folder = self.tmp / "csv_out_multi"
        multi = IatiOrganisationMultiCsvConverter()
        ok = multi.xml_to_csv_folder(in_xml, out_folder)
        self.assertTrue(ok, "xml_to_csv_folder devolvió False")

        names_csv = out_folder / "names.csv"
        self.assertTrue(names_csv.exists(), "Debe crearse names.csv con múltiples nombres")

        with names_csv.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        got = {(r.get("name", ""), r.get("language", "")) for r in rows}
        self.assertSetEqual(
            got,
            {
                ("Mi Organización", ""),
                ("My Organisation", "en"),
                ("Mon Organisation", "fr"),
            },
            f"Contenido inesperado en names.csv: {got}",
        )

    def test_csv_to_xml_missing_main_name_raises_value_error(self):
        """If 'Name' is missing in organisations.csv, should raise ValueError."""
        folder = self.tmp / "csv_in_bad"
        folder.mkdir()
        org_csv = folder / "organisations.csv"
        with org_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "Organisation Identifier", "Name", "Reporting Org Ref",
                "Reporting Org Type", "Reporting Org Name"
            ])
            # Name vacío:
            w.writerow(["ORG-123", "", "ORG-123", "40", "ORG-123"])

        out_xml = self.tmp / "bad.xml"
        conv = IatiOrganisationCSVConverter()
        with self.assertRaises(ValueError):
            conv.convert_folder_to_xml(folder, out_xml)

    def test_csv_to_xml_missing_xml_lang_logs_warning_and_defaults_to_en(self):
        """
        If 'xml_lang' is missing and there is no names.csv: should NOT fail.
        Should log WARNING and assume xml:lang='en' in the resulting XML.
        """
        folder = self.tmp / "csv_in_missing_lang"
        folder.mkdir()
        org_csv = folder / "organisations.csv"

        # organisations.csv without xml_lang and no names.csv
        with org_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "Organisation Identifier", "Name", "Reporting Org Ref",
                "Reporting Org Type", "Reporting Org Name", "Default Currency"
            ])
            w.writerow([
                "ORG-123", "Mi Organización", "ORG-123", "40", "Mi Organización", "USD"
            ])

        out_xml = self.tmp / "out_missing_lang.xml"
        conv = IatiOrganisationCSVConverter()

        # Capture WARNING and verify fallback
        with self.assertLogs('okfn_iati.organisation_xml_generator', level='WARNING') as log:
            result = conv.convert_folder_to_xml(folder, out_xml)

        # File was generated
        self.assertEqual(str(out_xml), result)
        self.assertTrue(out_xml.exists(), "XML should be generated even without xml_lang")

        # WARNING was logged for missing xml_lang
        self.assertTrue(
            any("Missing 'xml_lang'" in msg for msg in log.output),
            f"Expected WARNING not found in logs: {log.output}"
        )

        # XML should have xml:lang='en' by default
        root = ET.parse(out_xml).getroot()
        org = root.find("iati-organisation")
        self.assertIsNotNone(org, "<iati-organisation> should exist")
        self.assertEqual(
            org.get("{http://www.w3.org/XML/1998/namespace}lang"),
            "en",
            "Should apply fallback xml:lang='en' when missing in CSV"
        )
