import unittest
import os
import tempfile
from pathlib import Path

from okfn_iati.organisation_xml_generator import (
    IatiOrganisationCSVConverter,
    IatiOrganisationXMLGenerator,
)

class TestOrganisationXMLGenerator(unittest.TestCase):
    def setUp(self):
        """Crear un archivo temporal CSV de prueba."""
        self.converter = IatiOrganisationCSVConverter()
        self.generator = IatiOrganisationXMLGenerator()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_file = Path(self.temp_dir.name) / "test_org.csv"
        self.xml_file = Path(self.temp_dir.name) / "test_org.xml"

        # Generar plantilla CSV con ejemplos
        self.converter.generate_template(self.csv_file, with_examples=True)

    def tearDown(self):
        """Limpiar archivos temporales."""
        self.temp_dir.cleanup()

    def test_csv_template_generated(self):
        """Verificar que se genera el archivo CSV."""
        self.assertTrue(self.csv_file.exists(), "El archivo CSV no fue creado")

    def test_convert_csv_to_xml(self):
        """Convertir CSV a XML y validar contenido básico."""
        output_path = self.converter.convert_to_xml(self.csv_file, self.xml_file)
        self.assertTrue(Path(output_path).exists(), "El archivo XML no fue creado")

        # Leer contenido del XML generado
        with open(output_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Verificar que contiene elementos básicos de IATI
        self.assertIn("<iati-organisations", xml_content)
        self.assertIn("<iati-organisation", xml_content)
        self.assertIn("<organisation-identifier>", xml_content)

if __name__ == "__main__":
    unittest.main()
